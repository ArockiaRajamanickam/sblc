from __future__ import annotations
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.infrastructure.db.models import UserOrm, RolePermissionOrm, PermissionOrm

class PermissionService:
    def __init__(self, session: Session):
        self.session = session

    def has_permission(self, user_id: UUID, permission_code: str) -> bool:
        stmt = (
            select(PermissionOrm.code)
            .join(RolePermissionOrm, RolePermissionOrm.permission_id == PermissionOrm.id)
            .join(UserOrm, UserOrm.role_id == RolePermissionOrm.role_id)
            .where(UserOrm.id == user_id)
            .where(PermissionOrm.code == permission_code)
        )
        permission = self.session.scalars(stmt).first()
        return permission is not None

    def require_permission(self, user_id: UUID, permission_code: str):
        if not self.has_permission(user_id, permission_code):
            raise PermissionError(f"User {user_id} lacks required permission: {permission_code}")
