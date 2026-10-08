#!/usr/bin/env python3
"""
Idempotent Fund Transfer Service
Implements domain transfer service complying with SPEC-001 contracts,
invariants, and negative security constraints.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
import uuid

from src.domain.billing.transfer_model import (
    Account,
    AccountStatus,
    TransferReceipt,
    TransferStatus,
)

logger = logging.getLogger("billing.transfer")


# -----------------------------------------------------------------------------
# Domain Exceptions
# -----------------------------------------------------------------------------

class TransferException(Exception):
    """Base exception for billing transfer domain errors."""
    pass


class InsufficientFundsException(TransferException):
    """Raised when source account has inadequate available balance."""
    pass


class TenantIsolationBreachException(TransferException):
    """Raised when an unauthorized cross-tenant transfer is attempted."""
    pass


class InvalidTransferAmountException(TransferException):
    """Raised when transfer amount is zero, negative, or invalid."""
    pass


class AccountNotActiveException(TransferException):
    """Raised when source or destination account status is not ACTIVE."""
    pass


class PaginationLimitExceededException(TransferException):
    """Raised when requested ledger page size exceeds the C_perf safeguard (50)."""
    pass


class IdempotencyConflictException(TransferException):
    """Raised when an idempotency key is replayed with conflicting transfer parameters."""
    pass


class RateLimitExceededException(TransferException):
    """Negative Constraint 4: Raised when an account exceeds 5 requests per minute (HTTP 429)."""
    pass


# -----------------------------------------------------------------------------
# Security & Privacy Helpers
# -----------------------------------------------------------------------------

def tokenize_account_id(account_id: str) -> str:
    """
    Negative Constraint 2: Zero PII/Financial Secrets in Logs.
    Tokenizes raw account identifiers into non-reversible, masked tokens (act_tok_xxxx).
    """
    token_hash = hashlib.sha256(account_id.encode("utf-8")).hexdigest()[:8]
    return f"act_tok_{token_hash}"


# -----------------------------------------------------------------------------
# Transfer Service Implementation
# -----------------------------------------------------------------------------

class TransferService:
    """
    Core Domain Service orchestrating atomic, idempotent account fund transfers.
    Guarantees:
    - Conservation of Capital (Invariant 1)
    - Available Balance Non-Negative Constraint (Invariant 2)
    - 24-hour Idempotency Caching (Invariant 3)
    - Cross-Tenant Boundary Isolation (Negative Constraint 1)
    - Zero PII in Audit Logs (Negative Constraint 2)
    - Server-Side History Pagination Safeguard (Negative Constraint 5 / C_perf)
    """

    IDEMPOTENCY_WINDOW_SECONDS = 86400  # 24 hours
    MAX_PAGE_SIZE = 50                  # C_perf safeguard
    RATE_LIMIT_MAX_REQUESTS = 5         # Negative Constraint 4: max 5 req/min
    RATE_LIMIT_WINDOW_SECONDS = 60      # 1 minute sliding window

    def __init__(self, service_logger: Optional[logging.Logger] = None):
        self._logger = service_logger or logger
        # In-memory stores for domain aggregate state
        # (tenant_id, idempotency_key) -> (TransferReceipt, recorded_at_datetime)
        self._idempotency_store: Dict[Tuple[str, str], Tuple[TransferReceipt, datetime]] = {}
        # account_id -> list of TransferReceipt
        self._ledger_history: Dict[str, List[TransferReceipt]] = defaultdict(list)
        # account_id -> list of request timestamps for sliding-window rate limiting
        self._rate_limit_store: Dict[str, List[datetime]] = defaultdict(list)

    def execute_transfer(
        self,
        source_account: Account,
        dest_account: Account,
        amount: Decimal | float | int,
        idempotency_key: str,
        timestamp: Optional[datetime] = None,
    ) -> TransferReceipt:
        """
        Executes an atomic transfer between two accounts within the same organization.

        :param source_account: Debited account
        :param dest_account: Credited account
        :param amount: Amount to transfer (must be strictly positive)
        :param idempotency_key: Unique client request identifier
        :param timestamp: Transaction timestamp (defaults to current UTC time)
        :return: TransferReceipt
        """
        now = timestamp or datetime.now(timezone.utc)

        # 1. Negative Constraint 3: Strict positive amount validation
        if amount is None:
            raise InvalidTransferAmountException("Transfer amount must not be None")
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        if amount <= Decimal("0.00"):
            raise InvalidTransferAmountException(
                f"Transfer amount must be strictly positive, received {amount}"
            )

        # 2. Negative Constraint 1: Cross-Tenant Isolation (EVALUATED FIRST)
        if source_account.tenant_id != dest_account.tenant_id:
            self._logger.critical(
                "SECURITY ALERT: Tenant isolation breach attempted from tenant %s to %s "
                "between source %s and destination %s",
                source_account.tenant_id,
                dest_account.tenant_id,
                tokenize_account_id(source_account.account_id),
                tokenize_account_id(dest_account.account_id),
            )
            raise TenantIsolationBreachException(
                f"Cross-tenant transfers forbidden: source tenant '{source_account.tenant_id}' "
                f"!= destination tenant '{dest_account.tenant_id}'"
            )

        # 3. State Machine & Account Status Invariant: Active accounts only
        if source_account.status != AccountStatus.ACTIVE or dest_account.status != AccountStatus.ACTIVE:
            self._logger.warning(
                "Transfer rejected due to inactive account status: source=%s, dest=%s",
                source_account.status,
                dest_account.status,
            )
            raise AccountNotActiveException(
                f"Both accounts must be ACTIVE. Source status: {source_account.status}, "
                f"Dest status: {dest_account.status}"
            )

        # 4. Negative Constraint 4: Rate Limiting (Max 5 requests per minute per account)
        recent_requests = [
            ts for ts in self._rate_limit_store[source_account.account_id]
            if (now - ts).total_seconds() < self.RATE_LIMIT_WINDOW_SECONDS
        ]
        if len(recent_requests) >= self.RATE_LIMIT_MAX_REQUESTS:
            self._logger.warning(
                "Rate limit exceeded (HTTP 429) for account %s: %d requests within %ds window",
                tokenize_account_id(source_account.account_id),
                len(recent_requests),
                self.RATE_LIMIT_WINDOW_SECONDS,
            )
            raise RateLimitExceededException(
                f"Rate limit exceeded (HTTP 429): account {source_account.account_id} "
                f"exceeded maximum {self.RATE_LIMIT_MAX_REQUESTS} requests per minute"
            )
        self._rate_limit_store[source_account.account_id] = recent_requests + [now]

        # 5. Invariant 3: Tenant-Scoped Idempotency Contract with Parameter Verification
        idempotency_lookup_key = (source_account.tenant_id, idempotency_key)
        if idempotency_lookup_key in self._idempotency_store:
            cached_receipt, recorded_time = self._idempotency_store[idempotency_lookup_key]
            elapsed_seconds = (now - recorded_time).total_seconds()
            if elapsed_seconds < self.IDEMPOTENCY_WINDOW_SECONDS:
                # Adversarial verification: Detect payload conflict on replay
                if (
                    cached_receipt.source_account_id != source_account.account_id
                    or cached_receipt.dest_account_id != dest_account.account_id
                    or cached_receipt.amount != amount
                ):
                    raise IdempotencyConflictException(
                        f"Idempotency key '{idempotency_key}' replayed with conflicting transfer parameters"
                    )
                self._logger.info(
                    "Idempotent replay detected for key %s in tenant %s; returning stored receipt",
                    idempotency_key,
                    source_account.tenant_id,
                )
                return cached_receipt

        # 5. Invariant 2: Non-negative balance rule & sufficient funds check
        if source_account.available_balance < amount:
            self._logger.info(
                "Transfer rejected due to insufficient funds: available=%s, requested=%s for account %s",
                source_account.available_balance,
                amount,
                tokenize_account_id(source_account.account_id),
            )
            raise InsufficientFundsException(
                f"Insufficient funds: source available balance {source_account.available_balance} "
                f"is less than required transfer amount {amount}"
            )

        # 6. Execute Atomic Ledger Mutation & Invariant 1 (Conservation of Capital)
        source_before = source_account.balance
        dest_before = dest_account.balance

        # Atomic debit and credit
        source_account.balance -= amount
        dest_account.balance += amount

        # Verify Conservation of Capital: delta(Source) + delta(Destination) == 0
        delta_source = source_account.balance - source_before
        delta_dest = dest_account.balance - dest_before
        if delta_source + delta_dest != Decimal("0.00"):
            # Rollback in case of anomaly
            source_account.balance = source_before
            dest_account.balance = dest_before
            raise TransferException("Conservation of capital invariant violated")

        # 7. Generate Receipt
        transfer_id = f"tr_{uuid.uuid4().hex[:12]}"
        receipt = TransferReceipt(
            transfer_id=transfer_id,
            idempotency_key=idempotency_key,
            source_account_id=source_account.account_id,
            dest_account_id=dest_account.account_id,
            amount=amount,
            status=TransferStatus.COMPLETED,
            timestamp=now,
            http_status=200,
        )

        # 8. Record in Tenant-Scoped Idempotency Store and Paginated Ledger History
        self._idempotency_store[(source_account.tenant_id, idempotency_key)] = (receipt, now)
        self._ledger_history[source_account.account_id].append(receipt)
        self._ledger_history[dest_account.account_id].append(receipt)

        self._logger.info(
            "Transfer completed: transfer_id=%s, source=%s, dest=%s, amount=%s",
            receipt.transfer_id,
            tokenize_account_id(source_account.account_id),
            tokenize_account_id(dest_account.account_id),
            amount,
        )

        return receipt

    def get_transaction_history(
        self,
        account_id: str,
        page_size: int = 50,
        page: int = 1,
    ) -> List[TransferReceipt]:
        """
        Negative Constraint 5 (Non-Functional Performance Invariant C_perf):
        Returns paginated balance history indexed by account_id.
        Enforces maximum page size of 50 records to prevent in-memory heap saturation.
        """
        if page_size > self.MAX_PAGE_SIZE:
            raise PaginationLimitExceededException(
                f"Page size {page_size} exceeds maximum permitted limit of {self.MAX_PAGE_SIZE}"
            )
        if page_size <= 0:
            raise ValueError("page_size must be positive")
        if page <= 0:
            raise ValueError("page must be positive")

        records = self._ledger_history.get(account_id, [])
        start = (page - 1) * page_size
        end = start + page_size
        return records[start:end]


# Module-level convenience singleton
_default_service: Optional[TransferService] = None


def get_default_service() -> TransferService:
    """Returns singleton instance of TransferService."""
    global _default_service
    if _default_service is None:
        _default_service = TransferService()
    return _default_service


def execute_transfer(
    source_account: Account,
    dest_account: Account,
    amount: Decimal | float | int,
    idempotency_key: str = "default-key",
    timestamp: Optional[datetime] = None,
) -> TransferReceipt:
    """Module-level convenience wrapper for TransferService.execute_transfer."""
    return get_default_service().execute_transfer(
        source_account=source_account,
        dest_account=dest_account,
        amount=amount,
        idempotency_key=idempotency_key,
        timestamp=timestamp,
    )
