from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.infrastructure.repositories.sblc_repository import SBLCRepository
from app.domain.models import SBLC, Approval, SBLCAmendment

from app.application.services.compliance_service import ComplianceService

async def transition_sblc_status(db: Session, sblc_id: UUID, target_status: str, redis_client: Optional[redis.Redis] = None, actor_id: Optional[UUID] = None) -> SBLC:
    repo = SBLCRepository(db, redis_client)
    sblc = await repo.get_by_id(sblc_id)
    if not sblc:
        raise HTTPException(status_code=404, detail="SBLC not found")

    if actor_id:
        ComplianceService(db).validate_sovereignty(actor_id, sblc.ledger_id, "ledger")

    current_status = str(sblc.status)
    
    # Valid transitions (Banking Lifecycle)
    valid_transitions = {
        "draft": ["submitted", "closed"],
        "submitted": ["under_review", "closed"],
        "under_review": ["approved", "submitted", "closed"], # submitted = push back
        "approved": ["issued"],
        "issued": ["pending_amendment", "claim_submitted", "closed"],
        "pending_amendment": ["amended", "issued", "closed"], # issued = rejected
        "amended": ["pending_amendment", "claim_submitted", "closed"],
        "claim_submitted": ["claim_resolved", "issued", "closed"],
        "claim_resolved": ["closed"],
        "closed": []
    }

    if target_status not in valid_transitions.get(current_status, []):
        print(f"DEBUG: INVALID TRANSITION {current_status} -> {target_status}")
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid transition from {current_status} to {target_status}"
        )

    print(f"DEBUG: TRANSITIONING {current_status} -> {target_status} for {sblc_id}")
    # Perform specific logic per transition if needed
    if target_status == "issued":
        if not sblc.reference_number:
            raise HTTPException(status_code=400, detail="Reference number required to issue")
            
    sblc.status = target_status
    db.flush()
    
    # Audit log via crud function later or directly
    from app.infrastructure.audit import write_audit
    write_audit(
        db,
        event_type=f"sblc.status_updated",
        entity_type="sblc",
        entity_id=sblc.id,
        ledger_id=sblc.ledger_id,
        before={"status": current_status},
        after={"status": target_status}
    )
    
    return sblc

async def submit_for_approval(db: Session, sblc_id: UUID, approval_type: str, user_id: UUID, redis_client: Optional[redis.Redis] = None) -> Approval:
    """
    approval_type: 'issuance' or 'amendment'
    """
    # Sovereignty Check
    ComplianceService(db).validate_sovereignty(user_id, sblc_id, "sblc") # Wait, need to handle sblc entity type in ComplianceService
    """
    approval_type: 'issuance' or 'amendment'
    """
    repo = SBLCRepository(db, redis_client)
    sblc = await repo.get_by_id(sblc_id)
    if approval_type == "issuance":
        if str(sblc.status) != "submitted":
             raise HTTPException(status_code=400, detail="SBLC must be submitted to request review")
        await transition_sblc_status(db, sblc_id, "under_review", redis_client)
        
        # Create Approval request
        approval = await repo.create_approval(
            entity_type="sblc",
            entity_id=sblc_id,
            status="pending",
            step_name="Issuance Review"
        )
        return approval
        
    elif approval_type == "amendment":
        if str(sblc.status) not in ["issued", "amended"]:
             raise HTTPException(status_code=400, detail="SBLC must be issued or amended to request amendment")
        await transition_sblc_status(db, sblc_id, "pending_amendment", redis_client)
        
        approval = await repo.create_approval(
            entity_type="sblc",
            entity_id=sblc_id, 
            status="pending",
            step_name="Amendment Review"
        )
        return approval
        
    raise HTTPException(status_code=400, detail="Invalid approval type")

async def process_approval(db: Session, approval_id: UUID, decision: str, user_id: UUID, comments: str | None, redis_client: Optional[redis.Redis] = None) -> Approval:
    approval = db.get(Approval, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    # Sovereignty Check (Check if actor can approve this entity)
    # approval.entity_id is the SBLC ID if entity_type is 'sblc'
    ComplianceService(db).validate_sovereignty(user_id, approval.entity_id, approval.entity_type)
    
    if str(approval.status) != "pending":
         raise HTTPException(status_code=400, detail="Approval already processed")
         
    approval.status = decision
    approval.approver_user_id = user_id
    approval.comments = comments
    approval.updated_at = datetime.now(timezone.utc)
    db.flush()
    
    # Audit the decision
    from app.infrastructure.audit import write_audit
    write_audit(
        db,
        event_type="approval.decided",
        entity_type="approval",
        entity_id=approval.id,
        actor_user_id=user_id,
        after={"status": decision, "comments": comments}
    )
    
    # Check if we should transition the entity
    if decision == "approved":
        if approval.entity_type == "sblc":
            # For issuance workflow
            sblc_repo = SBLCRepository(db, redis_client)
            sblc = await sblc_repo.get_by_id(approval.entity_id)
            if sblc and str(sblc.status) == "under_review":
                 await transition_sblc_status(db, sblc.id, "approved", redis_client)
                 await transition_sblc_status(db, sblc.id, "issued", redis_client)
                 
                 # --- Blockchain Integration (Phase 5) ---
                 from app.infrastructure.worker import anchor_sblc_task
                 import json
                 import hashlib
                 
                 # 1. Compute Hash (Minimal PII)
                 state_data = {
                     "id": str(sblc.id),
                     "ref": sblc.reference_number,
                     "amt": str(sblc.amount),
                     "cur": sblc.currency,
                     "exp": str(sblc.expiry_date),
                     "status": str(sblc.status),
                     "law": sblc.governing_law,
                     "rules": sblc.applicable_rules
                 }
                 state_json = json.dumps(state_data, sort_keys=True)
                 state_hash = hashlib.sha256(state_json.encode()).hexdigest()
                 
                 # 2. Update SBLC to pending_anchor
                 sblc.onchain_status = "pending_anchor"
                 db.flush()
                 
                 # 3. Anchor (Async - Offload to Celery)
                 try:
                     anchor_sblc_task.delay(str(sblc.id), state_hash, sblc.tx_hash)
                     sblc.onchain_status = "pending_anchor"
                 except Exception as e:
                     print(f"Blockchain Error: {e}")
                     sblc.onchain_status = "failed"
                 
                 db.flush()

            elif sblc and str(sblc.status) == "pending_amendment":
                 # ... (rest of amendment logic)
                 # Apply amendment
                 # Find the pending amendment record
                 amendments = await sblc_repo.list_amendments(sblc.id)
                 if amendments and str(amendments[0].status) == "pending":
                     amendment = amendments[0]
                     amendment.status = "approved"
                     # Apply changes (naive impl: update amount/expiry)
                     if "amount" in amendment.new_values:
                         sblc.amount = amendment.new_values["amount"]
                     if "expiry_date" in amendment.new_values:
                         sblc.expiry_date = amendment.new_values["expiry_date"]
                     sblc.status = "amended" # Or back to Issued? 'amended' is fine.
                     sblc.onchain_status = "pending_anchor" # Mark for re-anchor
                     db.flush()

    elif decision == "rejected":
        if approval.entity_type == "sblc":
             sblc_repo = SBLCRepository(db, redis_client)
             sblc = await sblc_repo.get_by_id(approval.entity_id)
             if str(sblc.status) == "under_review":
                 await transition_sblc_status(db, sblc.id, "submitted", redis_client) # Revert to submitted
             elif str(sblc.status) == "pending_amendment":
                 await transition_sblc_status(db, sblc.id, "issued", redis_client) # Revert to issued
                 # Mark amendment rejected
                 amendments = await sblc_repo.list_amendments(sblc.id)
                 if amendments and str(amendments[0].status) == "pending":
                     amendments[0].status = "rejected"
                     db.flush()

    return approval
