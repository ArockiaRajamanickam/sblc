from __future__ import annotations
from uuid import UUID, uuid4
from decimal import Decimal
from typing import Optional
from app.domain.interfaces import WalletService
from app.domain.entities import Wallet
from app.domain.value_objects import CryptoAmount, WalletAddress

class MockWalletService(WalletService):
    async def create_wallet(self, organization_id: UUID) -> Wallet:
        return Wallet(
            id=uuid4(),
            organization_id=organization_id,
            address=f"0x{uuid4().hex[:40]}",
            chain="ethereum",
            balance=CryptoAmount("ethereum", Decimal("0"))
        )

    async def get_balance(self, wallet_id: UUID) -> CryptoAmount:
        return CryptoAmount("ethereum", Decimal("100.0"))

    async def initiate_transfer(self, from_wallet_id: UUID, to_address: WalletAddress, amount: CryptoAmount) -> str:
        return f"0x{uuid4().hex}"

    async def get_transaction_status(self, tx_hash: str) -> str:
        return "confirmed"
