from __future__ import annotations
import json
import hashlib
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domain.models import SBLC
from app.infrastructure.repositories.sblc_repository import SBLCRepository
from app.infrastructure.repositories.ledger_repository import LedgerRepository
from app.infrastructure.blockchain import blockchain_service
from app.api.schemas import SBLCCreate
from app.application.services.compliance_service import ComplianceService

class IssueSBLCUseCase:
    """
    Application Service/Use Case for Issuing an SBLC.
    Orchestrates validation, persistence, audit, and blockchain anchoring.
    """
    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        self.db = db
        self.sblc_repo = SBLCRepository(db, redis_client)
        self.ledger_repo = LedgerRepository(db)

    async def execute(self, ledger_id: UUID, payload: SBLCCreate, actor_id: UUID) -> SBLC:
        # 1. Validation
        ledger = self.ledger_repo.get_ledger(ledger_id)
        if not ledger:
            raise HTTPException(status_code=404, detail="Ledger not found")

        # Data Sovereignty Check
        ComplianceService(self.db).validate_sovereignty(actor_id, ledger_id, "ledger")

        # 2. Persistence
        sblc = await self.sblc_repo.create(
            ledger_id=ledger_id,
            issuing_node_id=payload.issuing_node_id,
            applicant_node_id=payload.applicant_node_id,
            beneficiary_node_id=payload.beneficiary_node_id,
            reference_number=payload.reference_number,
            amount=payload.amount,
            currency=payload.currency,
            expiry_date=payload.expiry_date,
            metadata_json=payload.metadata_json,
        )

        # 3. Blockchain Anchoring (Async step)
        state_dict = {
            "id": str(sblc.id),
            "ref": sblc.reference_number,
            "amount": str(sblc.amount),
            "status": str(sblc.status)
        }
        state_hash = hashlib.sha256(json.dumps(state_dict, sort_keys=True).encode()).hexdigest()
        
        try:
            # Offload to Celery worker (Async)
            from app.infrastructure.worker import anchor_sblc_task
            anchor_sblc_task.delay(str(sblc.id), state_hash, None)
            sblc.onchain_status = "pending_anchor"
        except Exception as e:
            sblc.onchain_status = "anchor_failed"
            print(f"Failed to queue blockchain task: {e}")

        self.db.commit()
        self.db.refresh(sblc)
        
        return sblc
