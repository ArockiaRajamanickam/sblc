from __future__ import annotations
import hashlib
import json
from datetime import datetime
from typing import Any, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from .db.models import AuditLogOrm

def calculate_hash(data: Dict[str, Any], previous_hash: str) -> str:
    payload_str = json.dumps(data, sort_keys=True, default=str)
    content = f"{payload_str}|{previous_hash}"
    return hashlib.sha256(content.encode()).hexdigest()

def write_audit(
    session: Session,
    *,
    actor_id: UUID,
    action_type: str,
    entity_type: str,
    entity_id: UUID,
    payload: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    device_id: Optional[str] = None,
) -> AuditLogOrm:
    # Get the last hash for the hash chain
    last_log_stmt = select(AuditLogOrm).order_by(desc(AuditLogOrm.timestamp)).limit(1)
    last_log = session.scalars(last_log_stmt).first()
    previous_hash = last_log.current_hash if last_log else "0" * 64
    
    current_payload = payload or {}
    new_hash = calculate_hash({
        "actor_id": str(actor_id),
        "action_type": action_type,
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "payload": current_payload,
        "timestamp": datetime.utcnow().isoformat()
    }, previous_hash)

    log = AuditLogOrm(
        actor_id=actor_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=current_payload,
        ip_address=ip_address,
        device_id=device_id,
        previous_hash=previous_hash,
        current_hash=new_hash
    )
    session.add(log)
    session.flush()
    return log
