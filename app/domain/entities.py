from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from decimal import Decimal

from .value_objects import Money, CryptoAmount, RiskScore, LoanTerm, InterestRate

class OrganizationType(Enum):
    COUNTRY = "country"
    BANK = "bank"
    INDIVIDUAL = "individual"

class LoanStatus(Enum):
    DRAFT = "DRAFT"
    DUE_DILIGENCE = "DUE_DILIGENCE"
    RISK_REVIEW = "RISK_REVIEW"
    COMPLIANCE_REVIEW = "COMPLIANCE_REVIEW"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FUNDING = "FUNDING"
    FUNDED = "FUNDED"
    SETTLED = "SETTLED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"

class ApprovalStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

@dataclass
class Permission:
    id: UUID
    code: str
    description: str

@dataclass
class Role:
    id: UUID
    name: str
    permissions: List[Permission] = field(default_factory=list)

@dataclass
class User:
    id: UUID
    email: str
    full_name: str
    role: Role
    organization_id: UUID
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Organization:
    id: UUID
    name: str
    org_type: OrganizationType
    country_code: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Approval:
    id: UUID
    loan_id: UUID
    approver_id: UUID
    level: int
    status: ApprovalStatus = ApprovalStatus.PENDING
    comments: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None

@dataclass
class Loan:
    id: UUID
    organization_id: UUID
    applicant_id: UUID
    beneficiary_id: UUID
    amount: Money
    term: LoanTerm
    interest_rate: InterestRate
    status: LoanStatus = LoanStatus.DRAFT
    risk_score: Optional[RiskScore] = None
    approvals: List[Approval] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

    def add_approval(self, approval: Approval):
        if approval.approver_id == self.applicant_id:
             raise ValueError("Applicant cannot approve own loan")
        
        # 4-eyes principle: Approver must be different from any previous approver
        current_approvers = {a.approver_id for a in self.approvals if a.status == ApprovalStatus.APPROVED}
        if approval.approver_id in current_approvers:
            raise ValueError("4-eyes principle violation: User has already approved this loan")
            
        self.approvals.append(approval)
        self.updated_at = datetime.utcnow()

    def is_fully_approved(self) -> bool:
        # Simplistic implementation: escalation thresholds can be added here
        # Example threshold: > $50M requires level 4 approval
        threshold = Money(Decimal("50000000"), "USD")
        approved_levels = {a.level for a in self.approvals if a.status == ApprovalStatus.APPROVED}
        
        if self.amount.amount > threshold.amount:
            return 4 in approved_levels and len(approved_levels) >= 2 # Multi-level check
        
        return len(approved_levels) >= 2 # Standard 4-eyes (2 unique levels/people)

    def transition_to(self, target_status: LoanStatus):
        valid_transitions = {
            LoanStatus.DRAFT: [LoanStatus.DUE_DILIGENCE, LoanStatus.CLOSED],
            LoanStatus.DUE_DILIGENCE: [LoanStatus.RISK_REVIEW, LoanStatus.REJECTED],
            LoanStatus.RISK_REVIEW: [LoanStatus.COMPLIANCE_REVIEW, LoanStatus.REJECTED],
            LoanStatus.COMPLIANCE_REVIEW: [LoanStatus.PENDING_APPROVAL, LoanStatus.REJECTED],
            LoanStatus.PENDING_APPROVAL: [LoanStatus.APPROVED, LoanStatus.REJECTED],
            LoanStatus.APPROVED: [LoanStatus.FUNDING],
            LoanStatus.FUNDING: [LoanStatus.FUNDED, LoanStatus.REJECTED],
            LoanStatus.FUNDED: [LoanStatus.SETTLED],
            LoanStatus.SETTLED: [LoanStatus.CLOSED],
            LoanStatus.CLOSED: [LoanStatus.ARCHIVED],
            LoanStatus.REJECTED: [LoanStatus.ARCHIVED],
        }

        if target_status not in valid_transitions.get(self.status, []):
            raise ValueError(f"Invalid transition from {self.status.value} to {target_status.value}")
        
        if target_status == LoanStatus.APPROVED:
             if not self.is_fully_approved():
                 raise ValueError("Loan cannot be approved without meeting all approval requirements")

        self.status = target_status
        self.updated_at = datetime.utcnow()

@dataclass
class Transaction:
    id: UUID
    loan_id: UUID
    amount: Money
    actor_id: UUID
    idempotency_key: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Wallet:
    id: UUID
    organization_id: UUID
    address: str
    chain: str
    balance: CryptoAmount

@dataclass
class ComplianceCheck:
    id: UUID
    organization_id: UUID
    status: str
    findings: str
    performed_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AuditLog:
    id: UUID
    actor_id: UUID
    action_type: str
    entity_type: str
    entity_id: UUID
    payload: Dict[str, Any]
    ip_address: str
    device_id: str
    previous_hash: str
    current_hash: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RiskAssessment:
    id: UUID
    loan_id: UUID
    score: RiskScore
    factors: Dict[str, Any]
    assessed_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Document:
    id: UUID
    loan_id: UUID
    title: str
    file_path: str
    file_hash: str
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
