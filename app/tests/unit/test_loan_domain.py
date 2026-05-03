import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime
from app.domain.entities import Loan, LoanStatus, Approval, ApprovalStatus
from app.domain.value_objects import Money, LoanTerm, InterestRate

def test_loan_state_machine_valid_transition():
    loan = Loan(
        id=uuid4(),
        organization_id=uuid4(),
        applicant_id=uuid4(),
        beneficiary_id=uuid4(),
        amount=Money(Decimal("1000"), "USD"),
        term=LoanTerm(12),
        interest_rate=InterestRate(Decimal("5.0")),
        status=LoanStatus.DRAFT
    )
    loan.transition_to(LoanStatus.DUE_DILIGENCE)
    assert loan.status == LoanStatus.DUE_DILIGENCE

def test_loan_state_machine_invalid_transition():
    loan = Loan(
        id=uuid4(),
        organization_id=uuid4(),
        applicant_id=uuid4(),
        beneficiary_id=uuid4(),
        amount=Money(Decimal("1000"), "USD"),
        term=LoanTerm(12),
        interest_rate=InterestRate(Decimal("5.0")),
        status=LoanStatus.DRAFT
    )
    with pytest.raises(ValueError, match="Invalid transition"):
        loan.transition_to(LoanStatus.FUNDED)

def test_loan_four_eyes_principle():
    loan = Loan(
        id=uuid4(),
        organization_id=uuid4(),
        applicant_id=uuid4(),
        beneficiary_id=uuid4(),
        amount=Money(Decimal("1000"), "USD"),
        term=LoanTerm(12),
        interest_rate=InterestRate(Decimal("5.0")),
        status=LoanStatus.PENDING_APPROVAL
    )
    
    user1 = uuid4()
    app1 = Approval(id=uuid4(), loan_id=loan.id, approver_id=user1, level=1, status=ApprovalStatus.APPROVED)
    loan.add_approval(app1)
    
    # Same user cannot approve again
    app2 = Approval(id=uuid4(), loan_id=loan.id, approver_id=user1, level=2, status=ApprovalStatus.APPROVED)
    with pytest.raises(ValueError, match="4-eyes principle violation"):
        loan.add_approval(app2)

def test_loan_approval_threshold():
    # > $50M requires level 4
    loan = Loan(
        id=uuid4(),
        organization_id=uuid4(),
        applicant_id=uuid4(),
        beneficiary_id=uuid4(),
        amount=Money(Decimal("60000000"), "USD"),
        term=LoanTerm(12),
        interest_rate=InterestRate(Decimal("5.0")),
        status=LoanStatus.PENDING_APPROVAL
    )
    
    # Level 1 and 2 approvals
    loan.add_approval(Approval(id=uuid4(), loan_id=loan.id, approver_id=uuid4(), level=1, status=ApprovalStatus.APPROVED))
    loan.add_approval(Approval(id=uuid4(), loan_id=loan.id, approver_id=uuid4(), level=2, status=ApprovalStatus.APPROVED))
    
    assert loan.is_fully_approved() is False
    
    # Add Level 4
    loan.add_approval(Approval(id=uuid4(), loan_id=loan.id, approver_id=uuid4(), level=4, status=ApprovalStatus.APPROVED))
    assert loan.is_fully_approved() is True
