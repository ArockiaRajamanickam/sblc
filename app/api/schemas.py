from __future__ import annotations

from datetime import datetime
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field

# --- Ledgers ---


# --- Ledgers ---
class LedgerCreate(BaseModel):
    name: str = Field(min_length=2)
    description: Optional[str] = None


class LedgerOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Nodes ---
class NodeCreate(BaseModel):
    legal_name: str
    display_name: Optional[str] = None
    node_type: str
    country_code: Optional[str] = Field(default=None, min_length=2, max_length=2)
    lei: Optional[str] = None


class NodeOut(BaseModel):
    id: UUID
    legal_name: str
    display_name: Optional[str]
    node_type: str
    country_code: Optional[str]
    lei: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Roles / Permissions ---
class RoleOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class PermissionOut(BaseModel):
    id: UUID
    code: str
    description: Optional[str]

    class Config:
        from_attributes = True


# --- Memberships ---
class MembershipCreate(BaseModel):
    node_id: UUID
    role_id: UUID
    status: str = "invited"


class MembershipOut(BaseModel):
    id: UUID
    ledger_id: UUID
    node_id: UUID
    role_id: UUID
    status: str
    joined_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Audit ---
class AuditOut(BaseModel):
    id: UUID
    ledger_id: Optional[UUID]
    actor_user_id: Optional[UUID]
    actor_node_id: Optional[UUID]
    event_type: str
    entity_type: str
    entity_id: UUID
    before_json: Optional[dict]
    after_json: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True
from decimal import Decimal

# --- SBLCs ---
# --- Organizations (formerly Nodes) ---
class OrganizationCreate(BaseModel):
    name: str
    org_type: Literal["country", "bank", "individual"]
    country_code: str = Field(min_length=2, max_length=2)

class OrganizationOut(BaseModel):
    id: UUID
    name: str
    org_type: str
    country_code: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Loans (formerly SBLCs) ---
class LoanCreate(BaseModel):
    organization_id: UUID
    applicant_id: UUID
    beneficiary_id: UUID
    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)
    term_months: int
    interest_rate: Decimal
    idempotency_key: str

class LoanOut(BaseModel):
    id: UUID
    organization_id: UUID
    applicant_id: UUID
    beneficiary_id: UUID
    amount: Decimal
    currency: str
    term_months: int
    interest_rate: Decimal
    status: str
    risk_score: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SBLCCreate(BaseModel):
    # Deprecated: use LoanCreate
    issuing_node_id: UUID
    applicant_node_id: UUID
    beneficiary_node_id: UUID
    reference_number: str
    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)
    expiry_date: datetime
    metadata_json: Optional[dict] = None

class SBLCOut(BaseModel):
    # Deprecated: use LoanOut
    id: UUID
    ledger_id: UUID
    issuing_node_id: UUID
    applicant_node_id: UUID
    beneficiary_node_id: UUID
    reference_number: str
    amount: Decimal
    currency: str
    expiry_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Claims ---
class ClaimCreate(BaseModel):
    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)
    documents_json: Optional[list] = []


class ClaimOut(BaseModel):
    id: UUID
    sblc_id: UUID
    amount: Decimal
    currency: str
    status: str
    submission_date: datetime
    documents_json: Optional[list]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Auth & Users ---
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    node_id: Optional[UUID] = None


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    node_id: Optional[UUID]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Approvals ---
class ApprovalDecision(BaseModel):
    status: str
    comments: Optional[str] = None


class ApprovalOut(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    approver_user_id: Optional[UUID]
    role_id: Optional[UUID]
    status: str
    step_name: Optional[str]
    comments: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Amendments ---
class SBLCAmendmentCreate(BaseModel):
    change_description: str
    new_values: dict


class SBLCAmendmentOut(BaseModel):
    id: UUID
    sblc_id: UUID
    change_description: str
    previous_values: Optional[dict]
    new_values: Optional[dict]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Attachments ---
class SBLCAttachmentCreate(BaseModel):
    filename: str
    file_type: str
    file_hash: str
    visibility: str = "internal"


class SBLCAttachmentOut(BaseModel):
    id: UUID
    sblc_id: UUID
    filename: str
    file_type: str
    file_hash: str
    visibility: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Banking & Compliance ---

class ExternalBankOut(BaseModel):
    id: UUID
    name: str
    swift_bic: Optional[str]
    hq_country: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AccountCreate(BaseModel):
    node_id: UUID
    account_number: str
    currency: str = Field(min_length=3, max_length=3)
    account_type: str = "master"
    parent_id: Optional[UUID] = None
    is_nostro: bool = False


class AccountOut(BaseModel):
    id: UUID
    node_id: UUID
    parent_id: Optional[UUID]
    account_number: str
    account_type: str
    currency: str
    balance: Decimal
    reserved_funds: Decimal
    is_nostro: bool
    is_active: bool
    compliance_score: int
    created_at: datetime

    class Config:
        from_attributes = True


class WireTransferCreate(BaseModel):
    sender_account_id: UUID
    receiver_account_id: UUID
    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)
    reference: Optional[str] = None


class WireTransferOut(BaseModel):
    id: UUID
    sender_account_id: UUID
    receiver_account_id: UUID
    amount: Decimal
    currency: str
    reference: Optional[str]
    status: str
    is_sanction_check_passed: Optional[bool]
    is_flagged: bool
    flag_reason: Optional[str]
    created_at: datetime
    execution_time: Optional[datetime]

    class Config:
        from_attributes = True


class CBPortalQueryOut(BaseModel):
    portal: str
    account_status: str
    allowance_limit_usd: str
    last_verified_cb: datetime


# --- Financial Instruments ---

class InstrumentCreate(BaseModel):
    name: str
    instrument_type: str
    issuer_node_id: UUID
    par_value: Decimal
    currency: str = Field(min_length=3, max_length=3)
    isin: Optional[str] = None
    maturity_date: Optional[datetime] = None
    coupon_rate: Optional[Decimal] = None
    is_national_debt: bool = False
    metadata_json: Optional[dict] = None


class InstrumentOut(BaseModel):
    id: UUID
    name: str
    instrument_type: str
    issuer_node_id: UUID
    par_value: Decimal
    currency: str
    isin: Optional[str]
    maturity_date: Optional[datetime]
    coupon_rate: Optional[Decimal]
    is_national_debt: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Digital Wallets ---

class WalletCreate(BaseModel):
    node_id: UUID
    wallet_type: str
    address: str
    metadata_json: Optional[dict] = None


class WalletOut(BaseModel):
    id: UUID
    node_id: UUID
    wallet_type: str
    address: str
    is_verified_by_bank: bool
    verifying_bank_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class WalletVerifyPayload(BaseModel):
    verifying_bank_id: UUID
