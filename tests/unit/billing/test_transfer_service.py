#!/usr/bin/env python3
"""
Unit and Contract Tests for Idempotent Fund Transfer Service
Derived strictly from SPEC-001 (Section 6 Executable Test Matrix & Section 4 Negative Constraints).
"""

import logging
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import sys
from pathlib import Path

# Add project root to sys.path to enable imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.domain.billing.transfer_model import (
    Account,
    AccountStatus,
    TransferReceipt,
    TransferStatus,
)
from src.domain.billing.transfer_service import (
    TransferService,
    InsufficientFundsException,
    TenantIsolationBreachException,
    InvalidTransferAmountException,
    AccountNotActiveException,
    PaginationLimitExceededException,
    IdempotencyConflictException,
    RateLimitExceededException,
)


class TestFundTransferServiceContract(unittest.TestCase):
    """
    Contract test suite strictly mapping to SPEC-001:
    - TC-TR-001 through TC-TR-006
    - Invariant 1 (Conservation of Capital)
    - Invariant 2 (Non-Negative Balance Rule)
    - Invariant 3 (Idempotency Contract within 24h window)
    - Negative Constraint 1 (No Cross-Tenant Transfers)
    - Negative Constraint 2 (Zero PII/Financial Secrets in Logs)
    - Negative Constraint 3 (Strict Parameterization / Positive Amounts Only)
    - Negative Constraint 4 (Active Accounts Only)
    - Negative Constraint 5 (Paginated Balance/Transaction History, Max 50 Records)
    """

    def setUp(self):
        self.service = TransferService()
        self.tenant_id = "tenant-enterprise-01"
        self.source_account = Account(
            account_id="ACC-SOURCE-1001",
            tenant_id=self.tenant_id,
            balance=Decimal("500.00"),
            status=AccountStatus.ACTIVE,
        )
        self.dest_account = Account(
            account_id="ACC-DEST-2002",
            tenant_id=self.tenant_id,
            balance=Decimal("200.00"),
            status=AccountStatus.ACTIVE,
        )

    # -------------------------------------------------------------------------
    # TC-TR-001: Happy Path Transfer
    # -------------------------------------------------------------------------
    def test_tc_tr_001_happy_path_transfer(self):
        """
        TC-TR-001: Valid accounts, source has $500, transfer $100.
        Expected: Source $400, Dest +$100 ($300), Status COMPLETED, HTTP 200 receipt.
        """
        source_initial = self.source_account.balance
        dest_initial = self.dest_account.balance
        transfer_amount = Decimal("100.00")

        receipt = self.service.execute_transfer(
            source_account=self.source_account,
            dest_account=self.dest_account,
            amount=transfer_amount,
            idempotency_key="idemp-key-001",
        )

        self.assertIsInstance(receipt, TransferReceipt)
        self.assertEqual(receipt.status, TransferStatus.COMPLETED)
        self.assertEqual(receipt.http_status, 200)
        self.assertEqual(self.source_account.balance, Decimal("400.00"))
        self.assertEqual(self.dest_account.balance, Decimal("300.00"))
        self.assertEqual(receipt.amount, transfer_amount)

        # Invariant 1: Delta Balance(Source) + Delta Balance(Destination) == 0
        delta_source = self.source_account.balance - source_initial
        delta_dest = self.dest_account.balance - dest_initial
        self.assertEqual(delta_source + delta_dest, Decimal("0.00"))

    # -------------------------------------------------------------------------
    # TC-TR-002: Insufficient Funds
    # -------------------------------------------------------------------------
    def test_tc_tr_002_insufficient_funds(self):
        """
        TC-TR-002: Source has $50, transfer $100.
        Expected: Throws InsufficientFundsException, zero balance change.
        """
        poor_source = Account(
            account_id="ACC-POOR-1002",
            tenant_id=self.tenant_id,
            balance=Decimal("50.00"),
            status=AccountStatus.ACTIVE,
        )
        dest_initial = self.dest_account.balance

        with self.assertRaises(InsufficientFundsException):
            self.service.execute_transfer(
                source_account=poor_source,
                dest_account=self.dest_account,
                amount=Decimal("100.00"),
                idempotency_key="idemp-key-002",
            )

        self.assertEqual(poor_source.balance, Decimal("50.00"))
        self.assertEqual(self.dest_account.balance, dest_initial)

    # -------------------------------------------------------------------------
    # TC-TR-003: Idempotent Replay
    # -------------------------------------------------------------------------
    def test_tc_tr_003_idempotent_replay(self):
        """
        TC-TR-003: Repeat TC-TR-001 with same idempotency_key.
        Expected: Returns identical receipt, balances unchanged after replay.
        """
        idempotency_key = "idemp-key-replay-003"
        transfer_amount = Decimal("100.00")

        # First execution
        receipt1 = self.service.execute_transfer(
            source_account=self.source_account,
            dest_account=self.dest_account,
            amount=transfer_amount,
            idempotency_key=idempotency_key,
        )
        self.assertEqual(receipt1.status, TransferStatus.COMPLETED)
        self.assertEqual(self.source_account.balance, Decimal("400.00"))
        self.assertEqual(self.dest_account.balance, Decimal("300.00"))

        # Replay with identical idempotency_key
        receipt2 = self.service.execute_transfer(
            source_account=self.source_account,
            dest_account=self.dest_account,
            amount=transfer_amount,
            idempotency_key=idempotency_key,
        )

        # Receipt must be identical
        self.assertEqual(receipt1.transfer_id, receipt2.transfer_id)
        self.assertEqual(receipt1.idempotency_key, receipt2.idempotency_key)
        self.assertEqual(receipt1.amount, receipt2.amount)
        self.assertEqual(receipt2.http_status, 200)

        # Balances must NOT be mutated a second time
        self.assertEqual(self.source_account.balance, Decimal("400.00"))
        self.assertEqual(self.dest_account.balance, Decimal("300.00"))

    # -------------------------------------------------------------------------
    # TC-TR-004: Cross-Tenant Breach
    # -------------------------------------------------------------------------
    def test_tc_tr_004_cross_tenant_breach(self):
        """
        TC-TR-004: Source tenant_id=A, Dest tenant_id=B.
        Expected: Throws TenantIsolationBreachException, logs security alert, zero balance change.
        """
        foreign_dest = Account(
            account_id="ACC-FOREIGN-9999",
            tenant_id="tenant-foreign-99",
            balance=Decimal("200.00"),
            status=AccountStatus.ACTIVE,
        )
        source_initial = self.source_account.balance
        dest_initial = foreign_dest.balance

        with self.assertLogs("billing.transfer", level="CRITICAL") as cm:
            with self.assertRaises(TenantIsolationBreachException):
                self.service.execute_transfer(
                    source_account=self.source_account,
                    dest_account=foreign_dest,
                    amount=Decimal("100.00"),
                    idempotency_key="idemp-key-004",
                )

        # Confirm security alert logged
        self.assertTrue(any("Tenant isolation breach" in msg for msg in cm.output))
        # Balances unchanged
        self.assertEqual(self.source_account.balance, source_initial)
        self.assertEqual(foreign_dest.balance, dest_initial)

    # -------------------------------------------------------------------------
    # TC-TR-005: Zero / Negative Amount
    # -------------------------------------------------------------------------
    def test_tc_tr_005_zero_and_negative_amount(self):
        """
        TC-TR-005: Amount = $0 or -$50.
        Expected: Throws InvalidTransferAmountException, zero balance change.
        """
        source_initial = self.source_account.balance
        dest_initial = self.dest_account.balance

        # Test zero amount
        with self.assertRaises(InvalidTransferAmountException):
            self.service.execute_transfer(
                source_account=self.source_account,
                dest_account=self.dest_account,
                amount=Decimal("0.00"),
                idempotency_key="idemp-key-zero",
            )

        # Test negative amount
        with self.assertRaises(InvalidTransferAmountException):
            self.service.execute_transfer(
                source_account=self.source_account,
                dest_account=self.dest_account,
                amount=Decimal("-50.00"),
                idempotency_key="idemp-key-negative",
            )

        self.assertEqual(self.source_account.balance, source_initial)
        self.assertEqual(self.dest_account.balance, dest_initial)

    # -------------------------------------------------------------------------
    # TC-TR-006: Inactive Destination
    # -------------------------------------------------------------------------
    def test_tc_tr_006_inactive_destination(self):
        """
        TC-TR-006: Dest account has status=FROZEN.
        Expected: Throws AccountNotActiveException, zero debit.
        """
        frozen_dest = Account(
            account_id="ACC-FROZEN-3003",
            tenant_id=self.tenant_id,
            balance=Decimal("200.00"),
            status=AccountStatus.FROZEN,
        )
        source_initial = self.source_account.balance

        with self.assertRaises(AccountNotActiveException):
            self.service.execute_transfer(
                source_account=self.source_account,
                dest_account=frozen_dest,
                amount=Decimal("100.00"),
                idempotency_key="idemp-key-006",
            )

        self.assertEqual(self.source_account.balance, source_initial)
        self.assertEqual(frozen_dest.balance, Decimal("200.00"))

    # -------------------------------------------------------------------------
    # Negative Constraint Tests & Invariants
    # -------------------------------------------------------------------------
    def test_inactive_source_account(self):
        """
        Negative Constraint 4: Inactive source account (SUSPENDED).
        Expected: Throws AccountNotActiveException, zero mutations.
        """
        suspended_source = Account(
            account_id="ACC-SUSPENDED-4004",
            tenant_id=self.tenant_id,
            balance=Decimal("500.00"),
            status=AccountStatus.SUSPENDED,
        )
        with self.assertRaises(AccountNotActiveException):
            self.service.execute_transfer(
                source_account=suspended_source,
                dest_account=self.dest_account,
                amount=Decimal("100.00"),
                idempotency_key="idemp-key-susp",
            )
        self.assertEqual(suspended_source.balance, Decimal("500.00"))
        self.assertEqual(self.dest_account.balance, Decimal("200.00"))

    def test_conservation_of_capital_multi_transfer(self):
        """
        Invariant 1: Delta Balance(Source) + Delta Balance(Destination) == 0 across multiple transfers.
        """
        initial_total = self.source_account.balance + self.dest_account.balance

        self.service.execute_transfer(self.source_account, self.dest_account, Decimal("50.00"), "idem-m-1")
        self.service.execute_transfer(self.source_account, self.dest_account, Decimal("75.00"), "idem-m-2")
        self.service.execute_transfer(self.dest_account, self.source_account, Decimal("25.00"), "idem-m-3")

        final_total = self.source_account.balance + self.dest_account.balance
        self.assertEqual(initial_total, final_total)

    def test_idempotency_expiry_after_24_hours(self):
        """
        Invariant 3: Idempotency cache is bound to a 24-hour window.
        A replay past 24 hours is treated as a new transaction.
        """
        t0 = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        key = "idemp-key-window"

        receipt1 = self.service.execute_transfer(
            self.source_account, self.dest_account, Decimal("50.00"), key, timestamp=t0
        )
        self.assertEqual(self.source_account.balance, Decimal("450.00"))

        # Replay at t0 + 23 hours: within window, should return identical receipt, no mutation
        t_within = t0 + timedelta(hours=23)
        receipt_within = self.service.execute_transfer(
            self.source_account, self.dest_account, Decimal("50.00"), key, timestamp=t_within
        )
        self.assertEqual(receipt1.transfer_id, receipt_within.transfer_id)
        self.assertEqual(self.source_account.balance, Decimal("450.00"))

        # Replay at t0 + 25 hours: past 24-hour window, treated as a new transfer
        t_past = t0 + timedelta(hours=25)
        receipt_past = self.service.execute_transfer(
            self.source_account, self.dest_account, Decimal("50.00"), key, timestamp=t_past
        )
        self.assertNotEqual(receipt1.transfer_id, receipt_past.transfer_id)
        self.assertEqual(self.source_account.balance, Decimal("400.00"))

    def test_negative_constraint_zero_pii_in_logs(self):
        """
        Negative Constraint 2: Zero PII/Financial Secrets in Logs.
        Plaintext bank account numbers must NEVER appear in logs; only tokenized IDs (act_tok_xxxx).
        """
        with self.assertLogs("billing.transfer", level="INFO") as cm:
            self.service.execute_transfer(
                source_account=self.source_account,
                dest_account=self.dest_account,
                amount=Decimal("50.00"),
                idempotency_key="idemp-key-pii",
            )

        full_logs = "\n".join(cm.output)
        # Ensure raw account numbers are NOT present
        self.assertNotIn("ACC-SOURCE-1001", full_logs)
        self.assertNotIn("ACC-DEST-2002", full_logs)
        # Ensure tokenized account identifier pattern is present
        self.assertIn("act_tok_", full_logs)

    def test_negative_constraint_pagination_safeguard(self):
        """
        Negative Constraint 5 (C_perf): Paginated transaction history (max page size 50).
        Requesting page_size > 50 must raise PaginationLimitExceededException.
        Normal queries must be bounded to at most 50 records.
        """
        # Execute 5 transfers to generate ledger history
        for i in range(5):
            self.service.execute_transfer(
                self.source_account,
                self.dest_account,
                Decimal("10.00"),
                f"idemp-page-{i}",
            )

        # Valid page size <= 50 succeeds
        history = self.service.get_transaction_history(self.source_account.account_id, page_size=50)
        self.assertLessEqual(len(history), 50)

        # Exceeding page size 50 must be rejected
        with self.assertRaises(PaginationLimitExceededException):
            self.service.get_transaction_history(self.source_account.account_id, page_size=51)

        with self.assertRaises(PaginationLimitExceededException):
            self.service.get_transaction_history(self.source_account.account_id, page_size=100)

    # -------------------------------------------------------------------------
    # Adversarial Security Tests (Gate 2 & Gate 3 Invariant Audits)
    # -------------------------------------------------------------------------
    def test_cross_tenant_idempotency_collision_rejected(self):
        """
        Adversarial Invariant Audit (Gate 2):
        Verify that Tenant B cannot hijack or bypass tenant isolation by replaying
        an idempotency key that was used by Tenant A.
        """
        # Tenant A executes a valid transfer
        key = "shared-cross-tenant-key"
        receipt_a = self.service.execute_transfer(
            self.source_account, self.dest_account, Decimal("50.00"), key
        )
        self.assertEqual(receipt_a.status, TransferStatus.COMPLETED)

        # Tenant B tries to execute a cross-tenant transfer with the same key
        tenant_b_source = Account(
            account_id="ACC-TENANT-B-1",
            tenant_id="TENANT-B",
            balance=Decimal("500.00"),
        )
        # Attempt transfer to Tenant A account using Tenant A's key
        with self.assertRaises(TenantIsolationBreachException):
            self.service.execute_transfer(
                tenant_b_source, self.dest_account, Decimal("50.00"), key
            )

    def test_idempotency_payload_mismatch_raises_conflict(self):
        """
        Adversarial Invariant Audit (Gate 2):
        Replaying the same idempotency key with conflicting transfer parameters
        (e.g., different amount or destination) must raise IdempotencyConflictException.
        """
        key = "idemp-key-conflict-check"
        self.service.execute_transfer(
            self.source_account, self.dest_account, Decimal("50.00"), key
        )

        # Same key, different amount -> conflict
        with self.assertRaises(IdempotencyConflictException):
            self.service.execute_transfer(
                self.source_account, self.dest_account, Decimal("99.00"), key
            )

    def test_rate_limit_exceeded_raises_429(self):
        """
        Negative Constraint 4: Maximum 5 transfer requests per minute per account.
        The 6th transfer within a 60-second window must raise RateLimitExceededException (HTTP 429).
        """
        account = Account(
            account_id="ACC-RATELIMIT-TEST",
            tenant_id=self.tenant_id,
            balance=Decimal("1000.00"),
        )
        dest = Account(
            account_id="ACC-RATELIMIT-DEST",
            tenant_id=self.tenant_id,
            balance=Decimal("1000.00"),
        )

        # First 5 transfers within 60s succeed
        for i in range(5):
            self.service.execute_transfer(
                account, dest, Decimal("10.00"), f"idemp-rl-{i}"
            )

        # 6th transfer must be rejected under Negative Constraint 4
        with self.assertRaises(RateLimitExceededException):
            self.service.execute_transfer(
                account, dest, Decimal("10.00"), "idemp-rl-6-rejected"
            )


if __name__ == "__main__":
    unittest.main()
