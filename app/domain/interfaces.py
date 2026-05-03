from abc import ABC, abstractmethod
from uuid import UUID
from .value_objects import CryptoAmount, WalletAddress
from .entities import Wallet

class WalletService(ABC):
    @abstractmethod
    async def create_wallet(self, organization_id: UUID) -> Wallet:
        pass

    @abstractmethod
    async def get_balance(self, wallet_id: UUID) -> CryptoAmount:
        pass

    @abstractmethod
    async def initiate_transfer(self, from_wallet_id: UUID, to_address: WalletAddress, amount: CryptoAmount) -> str:
        pass

    @abstractmethod
    async def get_transaction_status(self, tx_hash: str) -> str:
        pass
