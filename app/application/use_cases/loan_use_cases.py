from __future__ import annotations
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from decimal import Decimal

from app.domain.entities import Loan, Approval, LoanStatus, ApprovalStatus, User
from app.domain.value_objects import Money, LoanTerm, InterestRate, IdempotencyKey
from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.audit import write_audit
from app.infrastructure.db.models import IdempotencyKeyOrm

from app.application.services.permission_service import PermissionService
from app.application.services.compliance_engine import ComplianceEngine

class LoanUseCases:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.permissions = PermissionService(uow.session)
        self.compliance = ComplianceEngine(uow)

    async def create_loan(
        self,
        actor_id: UUID,
        organization_id: UUID,
        applicant_id: UUID,
        beneficiary_id: UUID,
        amount: Decimal,
        currency: str,
        term_months: int,
        interest_rate: Decimal,
        idempotency_key: str,
        ip_address: str
    ) -> Loan:
        # 0. Permission Check
        self.permissions.require_permission(actor_id, "loan.create")
        
        # 1. Idempotency Check
        # ... (rest of create_loan)
        existing_key = self.uow.session.get(IdempotencyKeyOrm, idempotency_key)
        if existing_key:
             raise ValueError("Duplicate idempotency key")
        
        # 2. Compliance Check (Sync for now, could be async task)
        is_cleared = await self.compliance.verify_organization(applicant_id)
        if not is_cleared:
            raise ValueError("Applicant organization is not compliance-cleared")

        loan = Loan(
            id=uuid4(),
            organization_id=organization_id,
            applicant_id=applicant_id,
            beneficiary_id=beneficiary_id,
            amount=Money(amount, currency),
            term=LoanTerm(term_months),
            interest_rate=InterestRate(interest_rate),
            status=LoanStatus.DRAFT
        )

        with self.uow:
            self.uow.loans.save(loan)
            ik = IdempotencyKeyOrm(key=idempotency_key)
            self.uow.session.add(ik)
            
            write_audit(
                self.uow.session,
                actor_id=actor_id,
                action_type="loan.created",
                entity_type="loan",
                entity_id=loan.id,
                payload={"amount": str(amount), "currency": currency},
                ip_address=ip_address
            )
            self.uow.commit()

        return loan

    async def approve_loan(
        self,
        actor_id: UUID,
        loan_id: UUID,
        level: int,
        decision: str,
        comments: Optional[str],
        ip_address: str
    ) -> Loan:
        # 0. Permission Check
        self.permissions.require_permission(actor_id, f"loan.approve_level_{level}")
        
        status_enum = ApprovalStatus.APPROVED if decision == "APPROVED" else ApprovalStatus.REJECTED

        with self.uow:
            loan = self.uow.loans.get_by_id(loan_id)
            if not loan:
                raise ValueError("Loan not found")

            # 3. Domain logic: Add approval
            approval = Approval(
                id=uuid4(),
                loan_id=loan_id,
                approver_id=actor_id,
                level=level,
                status=status_enum,
                comments=comments,
                decided_at=datetime.utcnow()
            )
            
            loan.add_approval(approval)
            # ... (rest of approve_loan)
            if status_enum == ApprovalStatus.APPROVED:
                try:
                    if loan.status == LoanStatus.PENDING_APPROVAL and loan.is_fully_approved():
                        loan.transition_to(LoanStatus.APPROVED)
                except ValueError:
                     pass
            elif status_enum == ApprovalStatus.REJECTED:
                loan.transition_to(LoanStatus.REJECTED)

            self.uow.loans.save(loan)
            
            write_audit(
                self.uow.session,
                actor_id=actor_id,
                action_type=f"loan.approval_{decision.lower()}",
                entity_type="loan",
                entity_id=loan.id,
                payload={"level": level, "comments": comments},
                ip_address=ip_address
            )
            self.uow.commit()

        return loan

    async def fund_loan(
        self,
        actor_id: UUID,
        loan_id: UUID,
        ip_address: str
    ) -> Loan:
        self.permissions.require_permission(actor_id, "loan.fund")
        
        with self.uow:
            loan = self.uow.loans.get_by_id(loan_id)
            if not loan or loan.status != LoanStatus.APPROVED:
                raise ValueError("Loan must be in APPROVED status to be funded")

            # 1. Transition to FUNDING
            loan.transition_to(LoanStatus.FUNDING)
            self.uow.loans.save(loan)
            self.uow.flush()

            # 2. Call Wallet Service (Mock)
            # In a real system, this would be an async task or a call to a custody provider
            # For simplicity, we assume it succeeds and move to FUNDED
            from app.infrastructure.crypto.mock_wallet_service import MockWalletService
            wallet_svc = MockWalletService()
            # wallet_svc.transfer(...)
            
            loan.transition_to(LoanStatus.FUNDED)
            self.uow.loans.save(loan)
            
            write_audit(
                self.uow.session,
                actor_id=actor_id,
                action_type="loan.funded",
                entity_type="loan",
                entity_id=loan.id,
                payload={"final_status": "FUNDED"},
                ip_address=ip_address
            )
            self.uow.commit()
            
        return loan

    async def settle_loan(
        self,
        actor_id: UUID,
        loan_id: UUID,
        ip_address: str
    ) -> Loan:
        self.permissions.require_permission(actor_id, "loan.settle")
        
        with self.uow:
            loan = self.uow.loans.get_by_id(loan_id)
            if not loan or loan.status != LoanStatus.FUNDED:
                raise ValueError("Loan must be in FUNDED status to be settled")

            loan.transition_to(LoanStatus.SETTLED)
            loan.transition_to(LoanStatus.CLOSED) # Auto-close after settlement
            self.uow.loans.save(loan)
            
            write_audit(
                self.uow.session,
                actor_id=actor_id,
                action_type="loan.settled",
                entity_type="loan",
                entity_id=loan.id,
                payload={"final_status": "CLOSED"},
                ip_address=ip_address
            )
            self.uow.commit()
            
        return loan
