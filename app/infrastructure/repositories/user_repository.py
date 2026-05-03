from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.domain.models import User, UserLedgerRole, Role
from app.infrastructure.audit import write_audit

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.scalar(select(User).where(User.email == email))

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return list(self.session.scalars(select(User).offset(skip).limit(limit)))

    def assign_ledger_role(self, user_id: UUID, ledger_id: UUID, role_id: UUID) -> UserLedgerRole:
        user_role = UserLedgerRole(user_id=user_id, ledger_id=ledger_id, role_id=role_id)
        self.session.add(user_role)
        self.session.flush()
        
        role = self.session.get(Role, role_id)
        write_audit(
            self.session,
            event_type="user_role.assigned",
            entity_type="user_ledger_role",
            entity_id=user_role.id,
            ledger_id=ledger_id,
            after={
                "user_id": str(user_id),
                "ledger_id": str(ledger_id),
                "role_id": str(role_id),
                "role_name": role.name if role else "unknown"
            }
        )
        return user_role
