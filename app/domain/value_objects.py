from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")

@dataclass(frozen=True)
class CryptoAmount:
    chain: str
    amount: Decimal

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Crypto amount cannot be negative")

@dataclass(frozen=True)
class InterestRate:
    percentage: Decimal

    def __post_init__(self):
        if self.percentage < 0:
            raise ValueError("Interest rate cannot be negative")

@dataclass(frozen=True)
class LoanTerm:
    months: int

    def __post_init__(self):
        if self.months <= 0:
            raise ValueError("Loan term must be positive")

@dataclass(frozen=True)
class RiskScore:
    value: int

    def __post_init__(self):
        if not (0 <= self.value <= 100):
            raise ValueError("Risk score must be between 0 and 100")

@dataclass(frozen=True)
class WalletAddress:
    address: str
    chain: str

    def __post_init__(self):
        if not self.address:
            raise ValueError("Wallet address cannot be empty")

@dataclass(frozen=True)
class ApprovalLevel:
    level: int

    def __post_init__(self):
        if self.level < 0:
            raise ValueError("Approval level cannot be negative")

@dataclass(frozen=True)
class IdempotencyKey:
    key: str

    def __post_init__(self):
        if not self.key:
            raise ValueError("Idempotency key cannot be empty")
        try:
            UUID(self.key)
        except ValueError:
             pass # Could be UUID or string, spec doesn't strictly enforce UUID
