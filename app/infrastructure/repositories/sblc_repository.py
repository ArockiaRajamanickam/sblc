import json
import redis.asyncio as redis
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.domain.models import SBLC, SBLCAttachment, SBLCAmendment, Approval
from app.infrastructure.audit import write_audit

class SBLCRepository:
    def __init__(self, session: Session, redis_client: Optional[redis.Redis] = None):
        self.session = session
        self.redis = redis_client
        self.cache_ttl = 300 # 5 minutes

    async def create(self, *, ledger_id: UUID, issuing_node_id: UUID, applicant_node_id: UUID, 
               beneficiary_node_id: UUID, reference_number: str, amount: Decimal, 
               currency: str, expiry_date: datetime, metadata_json: dict | None = None,
               governing_law: str | None = None, applicable_rules: str | None = None,
               product_type: str | None = None) -> SBLC:
        sblc = SBLC(
            ledger_id=ledger_id,
            issuing_node_id=issuing_node_id,
            applicant_node_id=applicant_node_id,
            beneficiary_node_id=beneficiary_node_id,
            reference_number=reference_number,
            amount=amount,
            currency=currency,
            expiry_date=expiry_date,
            metadata_json=metadata_json or {},
            governing_law=governing_law,
            applicable_rules=applicable_rules,
            product_type=product_type,
        )
        self.session.add(sblc)
        self.session.flush()

        write_audit(
            self.session,
            event_type="sblc.created",
            entity_type="sblc",
            entity_id=sblc.id,
            ledger_id=ledger_id,
            after={
                "reference_number": sblc.reference_number,
                "amount": str(sblc.amount),
                "currency": sblc.currency,
                "status": str(sblc.status),
            },
        )
        # No need to cache on create usually, but could if desired.
        return sblc

    async def get_by_id(self, sblc_id: UUID) -> Optional[SBLC]:
        cache_key = f"sblc:{sblc_id}"
        
        # 1. Try Cache
        if self.redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    # Convert strings back to objects
                    data["id"] = UUID(data["id"])
                    data["ledger_id"] = UUID(data["ledger_id"])
                    data["issuing_node_id"] = UUID(data["issuing_node_id"])
                    data["applicant_node_id"] = UUID(data["applicant_node_id"])
                    data["beneficiary_node_id"] = UUID(data["beneficiary_node_id"])
                    data["amount"] = Decimal(data["amount"])
                    data["expiry_date"] = datetime.fromisoformat(data["expiry_date"])
                    if data.get("created_at"): data["created_at"] = datetime.fromisoformat(data["created_at"])
                    if data.get("updated_at"): data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                    
                    return SBLC(**data)
            except Exception as e:
                print(f"Cache read error: {e}")

        # 2. Db Fallback
        sblc = self.session.get(SBLC, sblc_id)
        if sblc and sblc.deleted_at:
            return None
            
        # 3. Populate Cache
        if sblc and self.redis:
            try:
                sblc_dict = {
                    "id": str(sblc.id),
                    "ledger_id": str(sblc.ledger_id),
                    "issuing_node_id": str(sblc.issuing_node_id),
                    "applicant_node_id": str(sblc.applicant_node_id),
                    "beneficiary_node_id": str(sblc.beneficiary_node_id),
                    "reference_number": sblc.reference_number,
                    "amount": str(sblc.amount),
                    "currency": sblc.currency,
                    "expiry_date": sblc.expiry_date.isoformat(),
                    "status": sblc.status,
                    "metadata_json": sblc.metadata_json,
                    "onchain_status": sblc.onchain_status,
                    "tx_hash": sblc.tx_hash,
                    "governing_law": sblc.governing_law,
                    "applicable_rules": sblc.applicable_rules,
                    "product_type": sblc.product_type,
                    "created_at": sblc.created_at.isoformat() if sblc.created_at else None,
                    "updated_at": sblc.updated_at.isoformat() if sblc.updated_at else None,
                }
                await self.redis.setex(cache_key, self.cache_ttl, json.dumps(sblc_dict))
            except Exception as e:
                print(f"Cache write error: {e}")
                
        return sblc

    async def _invalidate_cache(self, sblc_id: UUID):
        if self.redis:
            await self.redis.delete(f"sblc:{sblc_id}")

    async def list_by_ledger(self, ledger_id: UUID, applicant_node_id: UUID | None = None,
                       beneficiary_node_id: UUID | None = None, skip: int = 0, limit: int = 100) -> List[SBLC]:
        q = select(SBLC).where(SBLC.ledger_id == ledger_id).where(SBLC.deleted_at == None)
        if applicant_node_id:
            q = q.where(SBLC.applicant_node_id == applicant_node_id)
        if beneficiary_node_id:
            q = q.where(SBLC.beneficiary_node_id == beneficiary_node_id)
        return list(self.session.scalars(q.order_by(SBLC.created_at.desc()).offset(skip).limit(limit)))

    async def delete(self, sblc_id: UUID) -> Optional[SBLC]:
        sblc = await self.get_by_id(sblc_id)
        if sblc:
            stmt = update(SBLC).where(SBLC.id == sblc_id).values(deleted_at=datetime.now(timezone.utc), is_active=False)
            self.session.execute(stmt)
            self.session.flush()
            write_audit(self.session, event_type="sblc.deleted", entity_type="sblc", entity_id=sblc_id, ledger_id=sblc.ledger_id)
            self.session.refresh(sblc)
            await self._invalidate_cache(sblc_id)
        return sblc

    # Attachments
    async def add_attachment(self, sblc_id: UUID, filename: str, file_hash: str, file_type: str | None = None, visibility: str = "internal") -> SBLCAttachment:
        sblc = await self.get_by_id(sblc_id)
        if not sblc: raise ValueError("SBLC not found")
        attachment = SBLCAttachment(sblc_id=sblc_id, filename=filename, file_type=file_type, file_hash=file_hash, visibility=visibility)
        self.session.add(attachment)
        self.session.flush()
        write_audit(self.session, event_type="sblc.attachment_uploaded", entity_type="sblc_attachment", entity_id=attachment.id, ledger_id=sblc.ledger_id)
        return attachment

    # Amendments
    async def create_amendment(self, sblc_id: UUID, change_description: str, new_values: dict) -> SBLCAmendment:
        amendment = SBLCAmendment(sblc_id=sblc_id, change_description=change_description, new_values=new_values)
        self.session.add(amendment)
        self.session.flush()
        return amendment

    async def list_amendments(self, sblc_id: UUID) -> List[SBLCAmendment]:
        q = select(SBLCAmendment).where(SBLCAmendment.sblc_id == sblc_id).order_by(SBLCAmendment.created_at.desc())
        return list(self.session.scalars(q))

    # Approvals
    async def create_approval(self, entity_type: str, entity_id: UUID, step_name: str, status: str = "pending") -> Approval:
        approval = Approval(entity_type=entity_type, entity_id=entity_id, step_name=step_name, status=status)
        self.session.add(approval)
        self.session.flush()
        return approval
