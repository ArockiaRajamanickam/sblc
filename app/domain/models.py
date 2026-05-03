from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


NodeType = ENUM(
    "issuer_bank",
    "advising_bank",
    "applicant",
    "beneficiary",
    "auditor",
    "regulator",
    "service_provider",
    name="node_type",
)

MembershipStatus = ENUM(
    "invited",
    "active",
    "suspended",
    "removed",
    name="membership_status",
)

SBLCStatus = ENUM(
    "draft",
    "submitted",
    "under_review",
    "approved",
    "issued",
    "pending_amendment",
    "amended",
    "claim_submitted",
    "claim_resolved",
    "closed",
    name="sblc_status",
)

ApprovalStatus = ENUM(
    "pending",
    "approved",
    "rejected",
    name="approval_status",
)

ClaimStatus = ENUM(
    "pending",
    "review_required",
    "accepted",
    "payment_approved",
    "rejected",
    name="claim_status",
)

OnChainStatus = ENUM(
    "not_anchored",
    "pending_anchor",
    "anchored",
    "failed",
    name="onchain_status",
)

AccountType = ENUM(
    "master",
    "sub_account",
    "nostro",
    name="account_type",
)

TransactionStatus = ENUM(
    "pending",
    "held_compliance",
    "cleared",
    "failed",
    name="transaction_status",
)

FinancialInstrumentType = ENUM(
    "debt",
    "fixed_income",
    "index",
    "national_debt",
    name="instrument_type",
)

WalletType = ENUM(
    "btc",
    "eth",
    "institutional_vault",
    name="wallet_type",
)


class Ledger(Base):
    __tablename__ = "ledgers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    network_id = Column(Text) # e.g. 'ethereum-sepolia', 'fabric-testnet'
    contract_address = Column(Text)
    region_id = Column(String(10), server_default="US") # Geographic fencing
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    memberships = relationship("LedgerMembership", back_populates="ledger")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    legal_name = Column(Text, nullable=False)
    display_name = Column(Text)
    node_type = Column(NodeType, nullable=False)
    country_code = Column(String(2))
    lei = Column(Text)
    blockchain_identity = Column(Text) # Wallet address or DID
    region_id = Column(String(10), server_default="US")
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    memberships = relationship("LedgerMembership", back_populates="node")
    users = relationship("User", back_populates="node")

    issued_sblcs = relationship("SBLC", foreign_keys="SBLC.issuing_node_id", back_populates="issuing_node")
    applicant_sblcs = relationship("SBLC", foreign_keys="SBLC.applicant_node_id", back_populates="applicant_node")
    beneficiary_sblcs = relationship("SBLC", foreign_keys="SBLC.beneficiary_node_id", back_populates="beneficiary_node")


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)

    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(Text, nullable=False, unique=True)
    description = Column(Text)

    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


class LedgerMembership(Base):
    __tablename__ = "ledger_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ledger_id = Column(UUID(as_uuid=True), ForeignKey("ledgers.id", ondelete="CASCADE"), nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    status = Column(MembershipStatus, nullable=False, server_default="invited")
    joined_at = Column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("ledger_id", "node_id", "role_id", name="uq_membership"),
    )

    ledger = relationship("Ledger", back_populates="memberships")
    node = relationship("Node", back_populates="memberships")
    role = relationship("Role")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, nullable=False, unique=True)
    full_name = Column(Text)
    hashed_password = Column(Text)
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="SET NULL"))
    region_id = Column(String(10), server_default="US")
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    node = relationship("Node", back_populates="users")


class UserLedgerRole(Base):
    __tablename__ = "user_ledger_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ledger_id = Column(UUID(as_uuid=True), ForeignKey("ledgers.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "ledger_id", "role_id", name="uq_user_ledger_role"),
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ledger_id = Column(UUID(as_uuid=True), ForeignKey("ledgers.id", ondelete="SET NULL"))
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    actor_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="SET NULL"))
    event_type = Column(Text, nullable=False)
    entity_type = Column(Text, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    before_json = Column(JSONB)
    after_json = Column(JSONB)
    ip_address = Column(Text)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class SBLC(Base):
    __tablename__ = "sblcs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ledger_id = Column(UUID(as_uuid=True), ForeignKey("ledgers.id", ondelete="CASCADE"), nullable=False)
    issuing_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    applicant_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    beneficiary_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    
    reference_number = Column(Text, nullable=False, unique=True)
    amount = Column(sa.Numeric(precision=20, scale=4), nullable=False)
    currency = Column(String(3), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(SBLCStatus, nullable=False, server_default="draft")
    metadata_json = Column(JSONB, server_default="{}")
    
    # Instrument Details
    governing_law = Column(Text) # e.g. 'English Law'
    applicable_rules = Column(Text) # e.g. 'UCP 600', 'URDG 758'
    product_type = Column(Text) # e.g. 'Financial', 'Performance'
    
    # Blockchain Audit
    onchain_status = Column(OnChainStatus, nullable=False, server_default="not_anchored")
    tx_hash = Column(Text)
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    ledger = relationship("Ledger")
    issuing_node = relationship("Node", foreign_keys=[issuing_node_id], back_populates="issued_sblcs")
    applicant_node = relationship("Node", foreign_keys=[applicant_node_id], back_populates="applicant_sblcs")
    beneficiary_node = relationship("Node", foreign_keys=[beneficiary_node_id], back_populates="beneficiary_sblcs")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sblc_id = Column(UUID(as_uuid=True), ForeignKey("sblcs.id", ondelete="CASCADE"), nullable=False)
    amount = Column(sa.Numeric(precision=20, scale=4), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(ClaimStatus, nullable=False, server_default="pending")
    submission_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    documents_json = Column(JSONB, server_default="[]")
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    sblc = relationship("SBLC", back_populates="claims")

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(Text, nullable=False)  # 'sblc', 'claim', 'amendment'
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    approver_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"))
    status = Column(ApprovalStatus, nullable=False, server_default="pending")
    step_name = Column(Text)
    comments = Column(Text)
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    approver = relationship("User")
    role = relationship("Role")


class SBLCAmendment(Base):
    __tablename__ = "sblc_amendments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sblc_id = Column(UUID(as_uuid=True), ForeignKey("sblcs.id", ondelete="CASCADE"), nullable=False)
    change_description = Column(Text, nullable=False)
    previous_values = Column(JSONB)
    new_values = Column(JSONB)
    status = Column(Text, nullable=False, server_default="pending") # pending, approved, rejected
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    sblc = relationship("SBLC", back_populates="amendments")

class SBLCAttachment(Base):
    __tablename__ = "sblc_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sblc_id = Column(UUID(as_uuid=True), ForeignKey("sblcs.id", ondelete="CASCADE"), nullable=False)
    filename = Column(Text, nullable=False)
    file_type = Column(Text)
    file_hash = Column(Text) # SHA-256 for auditability
    visibility = Column(Text, server_default="internal") # internal, public
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    sblc = relationship("SBLC", back_populates="attachments")

# Relationships
SBLC.claims = relationship("Claim", back_populates="sblc", cascade="all, delete-orphan")
SBLC.amendments = relationship("SBLCAmendment", back_populates="sblc", cascade="all, delete-orphan")
SBLC.attachments = relationship("SBLCAttachment", back_populates="sblc", cascade="all, delete-orphan")


class TokenRevocation(Base):
    __tablename__ = "token_revocations"
    
    jti = Column(UUID(as_uuid=True), primary_key=True) # JWT ID
    revoked_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)


class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, nullable=False, index=True)
    role_name = Column(Text, nullable=False)
    ledger_id = Column(UUID(as_uuid=True), ForeignKey("ledgers.id", ondelete="CASCADE"), nullable=False)
    token = Column(Text, unique=True, nullable=False)
    is_used = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    ledger = relationship("Ledger")


class ExternalBank(Base):
    __tablename__ = "external_banks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True) # DBS, Chase, etc.
    swift_bic = Column(String(11))
    hq_country = Column(String(2))
    api_endpoint = Column(Text)
    is_active = Column(Boolean, nullable=False, server_default="true")
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CentralBankGateway(Base):
    __tablename__ = "central_bank_gateways"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False) # Bank of England, Bank of China
    region_code = Column(String(5))
    portal_url = Column(Text)
    allowance_limit = Column(sa.Numeric(precision=20, scale=4))
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class InstitutionAccount(Base):
    __tablename__ = "institution_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("institution_accounts.id", ondelete="CASCADE"))
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    
    account_number = Column(String(34), nullable=False, unique=True) # IBAN format often
    account_type = Column(AccountType, nullable=False, server_default="master")
    currency = Column(String(3), nullable=False)
    
    balance = Column(sa.Numeric(precision=20, scale=4), nullable=False, server_default="0")
    reserved_funds = Column(sa.Numeric(precision=20, scale=4), nullable=False, server_default="0") # For holds/blocking
    
    is_nostro = Column(Boolean, server_default="false")
    is_active = Column(Boolean, server_default="true")
    compliance_score = Column(sa.Integer, server_default="100") # Risk metric
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    node = relationship("Node")
    parent = relationship("InstitutionAccount", remote_side=[id], backref="sub_accounts")


class WireTransaction(Base):
    __tablename__ = "wire_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_account_id = Column(UUID(as_uuid=True), ForeignKey("institution_accounts.id"))
    receiver_account_id = Column(UUID(as_uuid=True), ForeignKey("institution_accounts.id"))
    
    amount = Column(sa.Numeric(precision=20, scale=4), nullable=False)
    currency = Column(String(3), nullable=False)
    reference = Column(Text) # SWIFT/UETR reference
    
    status = Column(TransactionStatus, nullable=False, server_default="pending")
    compliance_check_id = Column(UUID(as_uuid=True))
    
    # Audit & Compliance Flags
    is_sanction_check_passed = Column(Boolean)
    is_flagged = Column(Boolean, server_default="false")
    flag_reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    execution_time = Column(DateTime(timezone=True))

    sender = relationship("InstitutionAccount", foreign_keys=[sender_account_id])
    receiver = relationship("InstitutionAccount", foreign_keys=[receiver_account_id])


class FinancialInstrument(Base):
    __tablename__ = "financial_instruments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    instrument_type = Column(FinancialInstrumentType, nullable=False)
    isin = Column(String(12), unique=True) # International Securities Identification Number
    
    issuer_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"))
    par_value = Column(sa.Numeric(precision=20, scale=4))
    currency = Column(String(3))
    
    maturity_date = Column(DateTime(timezone=True))
    coupon_rate = Column(sa.Numeric(precision=5, scale=4)) # Interest rate
    
    is_national_debt = Column(Boolean, server_default="false")
    metadata_json = Column(JSONB, server_default="{}")
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    issuer = relationship("Node")


class DigitalWallet(Base):
    __tablename__ = "digital_wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False)
    wallet_type = Column(WalletType, nullable=False)
    address = Column(Text, nullable=False, unique=True)
    
    # Institutional Verification
    is_verified_by_bank = Column(Boolean, server_default="false")
    verifying_bank_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"))
    
    metadata_json = Column(JSONB, server_default="{}") # Public keys, provider info
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    node = relationship("Node", foreign_keys=[node_id])
    verifying_bank = relationship("Node", foreign_keys=[verifying_bank_id])
