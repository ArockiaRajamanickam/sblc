import asyncio
import hashlib
import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("blockchain")
logger.setLevel(logging.INFO)

class BlockchainService:
    """
    Mock Blockchain Service.
    Simulates interaction with EVM or Fabric networks.
    Data is NOT stored permanently here (stateless mock), but we return strict formats.
    """
    
    async def deploy_ledger(self, ledger_id: uuid.UUID, network_id: str) -> str:
        """
        Simulate deploying a Smart Contract for a Ledger.
        Returns: contract_address (0x...)
        """
        logger.info(f"Deployed LedgerMock contract for {ledger_id} on {network_id}")
        await asyncio.sleep(1) # Simulate block time
        return f"0x{uuid.uuid4().hex}"

    async def register_identity(self, node_id: uuid.UUID) -> str:
        """
        Simulate creating a Wallet/DID for a Node.
        Returns: wallet_address (0x...) or did:sblc:...
        """
        logger.info(f"Registered identity for node {node_id}")
        await asyncio.sleep(0.5)
        return f"0x{uuid.uuid4().hex}"

    async def record_state(self, sblc_id: uuid.UUID, state_hash: str, prev_tx_hash: str | None) -> str:
        """
        Anchor a state transition on-chain.
        sblc_id: The ID of the asset.
        state_hash: Hash of the off-chain state (e.g. SHA256 of the SBLC JSON).
        prev_tx_hash: Link to previous state for lineage.
        
        Returns: transaction_hash (0x...)
        """
        logger.info(f"Anchoring state for SBLC {sblc_id}. Hash: {state_hash}")
        
        # Simulate Network Latency / Consensus
        await asyncio.sleep(2) 
        
        # Generate TX Hash
        tx_content = f"{sblc_id}{state_hash}{prev_tx_hash}{datetime.utcnow()}"
        tx_hash = "0x" + hashlib.sha256(tx_content.encode()).hexdigest()
        
        return tx_hash

# Singleton instance
blockchain_service = BlockchainService()
