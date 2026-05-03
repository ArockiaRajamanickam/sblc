from __future__ import annotations
from typing import Type
from sqlalchemy.orm import Session
from app.infrastructure.repositories.loan_repository import LoanRepository
from app.infrastructure.audit import write_audit
from app.infrastructure.repositories.organization_repository import OrganizationRepository

class UnitOfWork:
    def __init__(self, session: Session):
        self.session = session
        self.loans = LoanRepository(session)
        self.organizations = OrganizationRepository(session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def flush(self):
        self.session.flush()
