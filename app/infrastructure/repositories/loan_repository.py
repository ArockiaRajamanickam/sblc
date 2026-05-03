from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.domain.entities import Loan, Approval, Organization
from app.domain.value_objects import Money, LoanTerm, InterestRate, RiskScore
from ..db.models import LoanOrm, ApprovalOrm, OrganizationOrm

class LoanRepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, orm: LoanOrm) -> Loan:
        loan = Loan(
            id=orm.id,
            organization_id=orm.organization_id,
            applicant_id=orm.applicant_id,
            beneficiary_id=orm.beneficiary_id,
            amount=Money(orm.amount, orm.currency),
            term=LoanTerm(orm.term_months),
            interest_rate=InterestRate(orm.interest_rate),
            status=orm.status, # Should map to Enum ideally
            risk_score=RiskScore(orm.risk_score) if orm.risk_score is not None else None,
            version=orm.version,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )
        # Load approvals
        approvals_stmt = select(ApprovalOrm).where(ApprovalOrm.loan_id == orm.id)
        approvals_orm = self.session.scalars(approvals_stmt).all()
        for a_orm in approvals_orm:
            loan.approvals.append(Approval(
                id=a_orm.id,
                loan_id=a_orm.loan_id,
                approver_id=a_orm.approver_id,
                level=a_orm.level,
                status=a_orm.status,
                comments=a_orm.comments,
                created_at=a_orm.created_at,
                decided_at=a_orm.decided_at
            ))
        return loan

    def get_by_id(self, loan_id: UUID) -> Optional[Loan]:
        orm = self.session.get(LoanOrm, loan_id)
        if orm:
            return self._to_domain(orm)
        return None

    def save(self, loan: Loan):
        orm = self.session.get(LoanOrm, loan.id)
        if not orm:
            orm = LoanOrm(
                id=loan.id,
                organization_id=loan.organization_id,
                applicant_id=loan.applicant_id,
                beneficiary_id=loan.beneficiary_id,
                amount=loan.amount.amount,
                currency=loan.amount.currency,
                term_months=loan.term.months,
                interest_rate=loan.interest_rate.percentage,
                status=loan.status.value,
                risk_score=loan.risk_score.value if loan.risk_score else None,
                version=loan.version
            )
            self.session.add(orm)
        else:
            # Optimistic Locking check
            if orm.version != loan.version:
                raise RuntimeError("Stale data: Optimistic locking failure")
            
            orm.organization_id = loan.organization_id
            orm.applicant_id = loan.applicant_id
            orm.beneficiary_id = loan.beneficiary_id
            orm.amount = loan.amount.amount
            orm.currency = loan.amount.currency
            orm.term_months = loan.term.months
            orm.interest_rate = loan.interest_rate.percentage
            orm.status = loan.status.value
            orm.risk_score = loan.risk_score.value if loan.risk_score else None
            orm.version += 1 # Increment version
            loan.version = orm.version

        # Sync Approvals
        # (Simplified: clear and re-insert or diff)
        self.session.query(ApprovalOrm).filter(ApprovalOrm.loan_id == loan.id).delete()
        for app in loan.approvals:
            app_orm = ApprovalOrm(
                id=app.id,
                loan_id=loan.id,
                approver_id=app.approver_id,
                level=app.level,
                status=app.status.value,
                comments=app.comments,
                created_at=app.created_at,
                decided_at=app.decided_at
            )
            self.session.add(app_orm)
        
        self.session.flush()
