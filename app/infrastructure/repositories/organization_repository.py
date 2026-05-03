from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.entities import Organization, OrganizationType
from ..db.models import OrganizationOrm

class OrganizationRepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, orm: OrganizationOrm) -> Organization:
        return Organization(
            id=orm.id,
            name=orm.name,
            org_type=OrganizationType(orm.org_type),
            country_code=orm.country_code,
            is_active=orm.is_active,
            created_at=orm.created_at
        )

    def get_by_id(self, org_id: UUID) -> Optional[Organization]:
        orm = self.session.get(OrganizationOrm, org_id)
        if orm:
            return self._to_domain(orm)
        return None

    def save(self, org: Organization):
        orm = self.session.get(OrganizationOrm, org.id)
        if not orm:
            orm = OrganizationOrm(
                id=org.id,
                name=org.name,
                org_type=org.org_type.value,
                country_code=org.country_code,
                is_active=org.is_active,
                created_at=org.created_at
            )
            self.session.add(orm)
        else:
            orm.name = org.name
            orm.org_type = org.org_type.value
            orm.country_code = org.country_code
            orm.is_active = org.is_active
        self.session.flush()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        stmt = select(OrganizationOrm).offset(skip).limit(limit)
        return [self._to_domain(orm) for orm in self.session.scalars(stmt).all()]
