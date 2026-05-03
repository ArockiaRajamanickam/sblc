from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.models import DigitalWallet, Node

class DigitalWalletService:
    def __init__(self, db: Session):
        self.db = db

    def register_wallet(
        self,
        node_id: UUID,
        wallet_type: str,
        address: str,
        metadata_json: Optional[dict] = None
    ) -> DigitalWallet:
        wallet = DigitalWallet(
            node_id=node_id,
            wallet_type=wallet_type,
            address=address,
            metadata_json=metadata_json or {}
        )
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def verify_wallet(self, wallet_id: UUID, verifying_bank_id: UUID) -> DigitalWallet:
        wallet = self.db.get(DigitalWallet, wallet_id)
        if not wallet:
            raise ValueError("Wallet not found")
        
        wallet.is_verified_by_bank = True
        wallet.verifying_bank_id = verifying_bank_id
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def get_wallets_for_node(self, node_id: UUID) -> List[DigitalWallet]:
        return self.db.scalars(
            select(DigitalWallet).where(DigitalWallet.node_id == node_id)
        ).all()

    def list_all_wallets(self) -> List[DigitalWallet]:
        return self.db.scalars(select(DigitalWallet)).all()
