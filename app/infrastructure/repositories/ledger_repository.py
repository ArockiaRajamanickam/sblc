from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.domain.models import Ledger, LedgerMembership, Node, Role
from app.infrastructure.audit import write_audit

class LedgerRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_ledger(self, *, name: str, description: str | None) -> Ledger:
        ledger = Ledger(name=name, description=description)
        self.session.add(ledger)
        self.session.flush()
        write_audit(self.session, event_type="ledger.created", entity_type="ledger", entity_id=ledger.id, ledger_id=ledger.id)
        return ledger

    def get_ledger(self, ledger_id: UUID) -> Optional[Ledger]:
        ledger = self.session.get(Ledger, ledger_id)
        if ledger and ledger.deleted_at:
            return None
        return ledger

    def list_ledgers(self, skip: int = 0, limit: int = 100) -> List[Ledger]:
        q = select(Ledger).where(Ledger.deleted_at == None).order_by(Ledger.created_at.desc()).offset(skip).limit(limit)
        return list(self.session.scalars(q))

    def delete_ledger(self, ledger_id: UUID) -> Optional[Ledger]:
        ledger = self.get_ledger(ledger_id)
        if ledger:
            stmt = update(Ledger).where(Ledger.id == ledger_id).values(deleted_at=datetime.now(timezone.utc), is_active=False)
            self.session.execute(stmt)
            self.session.flush()
            write_audit(self.session, event_type="ledger.deleted", entity_type="ledger", entity_id=ledger_id, ledger_id=ledger_id)
            self.session.refresh(ledger)
        return ledger

    # Node Management
    def create_node(self, *, legal_name: str, display_name: str | None, node_type: str, 
                    country_code: str | None = None, lei: str | None = None) -> Node:
        node = Node(legal_name=legal_name, display_name=display_name, node_type=node_type, 
                    country_code=country_code, lei=lei)
        self.session.add(node)
        self.session.flush()
        write_audit(self.session, event_type="node.created", entity_type="node", entity_id=node.id)
        return node

    def get_node(self, node_id: UUID) -> Optional[Node]:
        node = self.session.get(Node, node_id)
        if node and node.deleted_at:
            return None
        return node

    def list_nodes(self, skip: int = 0, limit: int = 100) -> List[Node]:
        q = select(Node).where(Node.deleted_at == None).order_by(Node.created_at.desc()).offset(skip).limit(limit)
        return list(self.session.scalars(q))

    def delete_node(self, node_id: UUID) -> Optional[Node]:
        node = self.get_node(node_id)
        if node:
            stmt = update(Node).where(Node.id == node_id).values(deleted_at=datetime.now(timezone.utc), is_active=False)
            self.session.execute(stmt)
            self.session.flush()
            write_audit(self.session, event_type="node.deleted", entity_type="node", entity_id=node_id)
            self.session.refresh(node)
        return node

    # Memberships
    def add_membership(self, ledger_id: UUID, node_id: UUID, role_id: UUID, status: str = "invited") -> LedgerMembership:
        membership = LedgerMembership(ledger_id=ledger_id, node_id=node_id, role_id=role_id, status=status, 
                                      joined_at=(datetime.now(timezone.utc) if status == "active" else None))
        self.session.add(membership)
        self.session.flush()
        write_audit(self.session, event_type="membership.created", entity_type="ledger_membership", entity_id=membership.id, ledger_id=ledger_id)
        return membership

    def list_memberships(self, ledger_id: UUID, skip: int = 0, limit: int = 100) -> List[LedgerMembership]:
        q = select(LedgerMembership).where(LedgerMembership.ledger_id == ledger_id).offset(skip).limit(limit)
        return list(self.session.scalars(q))
