from __future__ import annotations
from typing import List, Optional
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.models import (
    InstitutionAccount, 
    WireTransaction, 
    ExternalBank, 
    CentralBankGateway,
    TransactionStatus
)

class BankingService:
    def __init__(self, db: Session):
        self.db = db

    def create_account(
        self, 
        node_id: UUID, 
        account_number: str, 
        currency: str, 
        account_type: str = "master",
        parent_id: Optional[UUID] = None,
        is_nostro: bool = False
    ) -> InstitutionAccount:
        account = InstitutionAccount(
            node_id=node_id,
            account_number=account_number,
            currency=currency,
            account_type=account_type,
            parent_id=parent_id,
            is_nostro=is_nostro
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def initiate_wire_transfer(
        self, 
        sender_id: UUID, 
        receiver_id: UUID, 
        amount: Decimal, 
        currency: str, 
        reference: Optional[str] = None
    ) -> WireTransaction:
        sender = self.db.get(InstitutionAccount, sender_id)
        if not sender or sender.balance < amount:
            raise ValueError("Insufficient balance or sender account not found")

        # 1. Block funds on sender side
        sender.balance -= amount
        sender.reserved_funds += amount
        
        # 2. Create transaction record
        tx = WireTransaction(
            sender_account_id=sender_id,
            receiver_account_id=receiver_id,
            amount=amount,
            currency=currency,
            reference=reference,
            status="pending"
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def confirm_transfer(self, tx_id: UUID):
        tx = self.db.get(WireTransaction, tx_id)
        if not tx or tx.status != "pending":
             return

        sender = tx.sender
        receiver = tx.receiver
        
        # Move funds from reserved to receiver
        sender.reserved_funds -= tx.amount
        receiver.balance += tx.amount
        
        tx.status = "cleared"
        tx.execution_time = datetime.now(timezone.utc)
        self.db.commit()

    def block_funds(self, account_id: UUID, amount: Decimal, reason: str):
        account = self.db.get(InstitutionAccount, account_id)
        if not account or account.balance < amount:
            raise ValueError("Insufficient funds to block")
        
        account.balance -= amount
        account.reserved_funds += amount
        # Log this in a more robust system (Audit events elsewhere)
        self.db.commit()

    def get_account_hierarchy(self, master_id: UUID) -> List[InstitutionAccount]:
        return self.db.execute(
            select(InstitutionAccount).where(InstitutionAccount.parent_id == master_id)
        ).scalars().all()

    def seed_external_banks(self):
        banks = [
            {"name": "DBS Bank", "swift_bic": "DBSSSGGSXXX", "hq_country": "SG"},
            {"name": "US Bank", "swift_bic": "USBKUS44XXX", "hq_country": "US"},
            {"name": "JPMorgan Chase", "swift_bic": "CHASUS33XXX", "hq_country": "US"},
            {"name": "Wells Fargo", "swift_bic": "WELSUS66XXX", "hq_country": "US"},
            {"name": "BNY Mellon", "swift_bic": "BNYMUS33XXX", "hq_country": "US"},
            {"name": "Barclays", "swift_bic": "BARCGB22XXX", "hq_country": "GB"},
            {"name": "Bank of England", "swift_bic": "BKENGG22XXX", "hq_country": "GB"},
        ]
        for b_data in banks:
            existing = self.db.execute(select(ExternalBank).where(ExternalBank.name == b_data["name"])).scalar()
            if not existing:
                bank = ExternalBank(**b_data)
                self.db.add(bank)
        self.db.commit()
