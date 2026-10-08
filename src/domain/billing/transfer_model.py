#!/usr/bin/env python3
"""
Domain Model for Idempotent Fund Transfer Service
Implements domain entities, enums, and data models specified in SPEC-001.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import uuid


class AccountStatus(str, Enum):
    """Lifecycle status of a financial account."""
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"

    def __str__(self) -> str:
        return self.value


class TransferStatus(str, Enum):
    """State machine states for a fund transfer request."""
    INITIATED = "INITIATED"
    VALIDATED = "VALIDATED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return self.value


@dataclass
class Account:
    """
    Financial Account Aggregate Root.
    Enforces balance precision and status rules.
    """
    account_id: str
    tenant_id: str
    balance: Decimal
    status: AccountStatus = AccountStatus.ACTIVE

    def __post_init__(self):
        if not isinstance(self.balance, Decimal):
            self.balance = Decimal(str(self.balance))
        if isinstance(self.status, str) and not isinstance(self.status, AccountStatus):
            try:
                self.status = AccountStatus(self.status)
            except ValueError:
                pass

    @property
    def available_balance(self) -> Decimal:
        """Returns the funds available for debiting."""
        return self.balance


@dataclass
class TransferReceipt:
    """
    Immutable receipt returned upon successful or idempotent transfer execution.
    """
    transfer_id: str
    idempotency_key: str
    source_account_id: str
    dest_account_id: str
    amount: Decimal
    status: TransferStatus = TransferStatus.COMPLETED
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    http_status: int = 200

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))
        if isinstance(self.status, str) and not isinstance(self.status, TransferStatus):
            try:
                self.status = TransferStatus(self.status)
            except ValueError:
                pass
