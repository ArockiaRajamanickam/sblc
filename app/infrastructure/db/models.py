from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Numeric, Integer, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class OrganizationOrm(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    org_type = Column(String, nullable=False) # country, bank, individual
    country_code = Column(String(2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PermissionOrm(Base):
    __tablename__ = "permissions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    description = Column(Text)

class RoleOrm(Base):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    
class RolePermissionOrm(Base):
    __tablename__ = "role_permissions"
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)

class UserOrm(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LoanOrm(Base):
    __tablename__ = "loans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    beneficiary_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    amount = Column(Numeric(20, 4), nullable=False)
    currency = Column(String(3), nullable=False)
    term_months = Column(Integer, nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    status = Column(String, nullable=False)
    risk_score = Column(Integer)
    version = Column(Integer, default=1) # Optimistic locking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ApprovalOrm(Base):
    __tablename__ = "approvals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"))
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    level = Column(Integer, nullable=False)
    status = Column(String, nullable=False) # PENDING, APPROVED, REJECTED
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime)

class AuditLogOrm(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    payload = Column(JSONB)
    ip_address = Column(String)
    device_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    previous_hash = Column(String)
    current_hash = Column(String)

class TransactionOrm(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"))
    amount = Column(Numeric(20, 4), nullable=False)
    currency = Column(String(3), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    idempotency_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class WalletOrm(Base):
    __tablename__ = "wallets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    address = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    balance_amount = Column(Numeric(20, 4), nullable=False)
    balance_chain = Column(String, nullable=False)

class ComplianceCheckOrm(Base):
    __tablename__ = "compliance_checks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    status = Column(String, nullable=False)
    findings = Column(Text)
    performed_at = Column(DateTime, default=datetime.utcnow)

class RiskAssessmentOrm(Base):
    __tablename__ = "risk_assessments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"))
    score = Column(Integer, nullable=False)
    factors = Column(JSONB)
    assessed_at = Column(DateTime, default=datetime.utcnow)

class DocumentOrm(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"))
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class IdempotencyKeyOrm(Base):
    __tablename__ = "idempotency_keys"
    key = Column(String, primary_key=True)
    response_body = Column(JSONB)
    status_code = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
