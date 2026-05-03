from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func
import sqlalchemy as sa
from typing import List, Optional
import json
import secrets
from datetime import datetime, timezone, timedelta
from uuid import UUID

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

from app.infrastructure.db import SessionLocal, settings
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.sblc_repository import SBLCRepository
from app.infrastructure.repositories.ledger_repository import LedgerRepository
from app.application.use_cases.issue_sblc import IssueSBLCUseCase
from app.domain.models import User, SBLC, Node, Ledger, Role, Invitation, UserLedgerRole, AuditEvent, TokenRevocation, SBLCAttachment
from app.api.schemas import (
    AuditOut,
    LedgerCreate,
    LedgerOut,
    MembershipCreate,
    MembershipOut,
    NodeCreate,
    NodeOut,
    PermissionOut,
    RoleOut,
    SBLCCreate,
    SBLCOut,
    ClaimCreate,
    ClaimOut,
    Token,
    UserCreate,
    UserOut,
    ApprovalDecision,
    ApprovalOut,
    SBLCAmendmentCreate,
    SBLCAmendmentOut,
    SBLCAttachmentCreate,
    SBLCAttachmentOut,
    OrganizationCreate,
    OrganizationOut,
    LoanCreate,
    LoanOut,
    AccountCreate,
    AccountOut,
    WireTransferCreate,
    WireTransferOut,
    CBPortalQueryOut,
    InstrumentCreate,
    InstrumentOut,
    WalletCreate,
    WalletOut,
    WalletVerifyPayload,
)
from app.application.sblc_logic import transition_sblc_status, submit_for_approval, process_approval
from app.infrastructure.security.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    # create_refresh_token,  # deprecated in favor of create_tokens
    create_tokens,
    refresh_access_token,
    get_current_user,
    require_permission, 
    ActorInfo
)
from app.infrastructure.security.redis_client import get_redis
import redis.asyncio as redis
from fastapi.security import OAuth2PasswordRequestForm
from app.infrastructure.audit import write_audit
from app.infrastructure.middleware import CorrelationIdMiddleware, rate_limit_auth
from app.infrastructure.security.idempotency import IdempotencyMiddleware
from app.infrastructure.db.uow import UnitOfWork
from app.application.use_cases.loan_use_cases import LoanUseCases

from app.infrastructure.security.anomaly_detection import AnomalyDetectionMiddleware
from app.infrastructure.security.redis_client import get_redis_sync # Assume a sync helper for middleware or use async properly

# Setup Redis for middleware (simulated sync for app.add_middleware)
import redis
r_client = redis.from_url(settings.redis_url)

app = FastAPI(title="SBLC Financial Infrastructure API", version="0.2.0")

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(IdempotencyMiddleware)
app.add_middleware(AnomalyDetectionMiddleware, redis_client=r_client)
app.middleware("http")(rate_limit_auth)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_uow(db: Session = Depends(get_db)):
    return UnitOfWork(db)


from app.application.services.banking_service import BankingService
from app.application.services.compliance_service import ComplianceService
from app.application.services.instrument_service import FinancialInstrumentService
from app.application.services.digital_wallet_service import DigitalWalletService

def get_banking_service(db: Session = Depends(get_db)):
    return BankingService(db)

def get_compliance_service(db: Session = Depends(get_db)):
    return ComplianceService(db)

def get_instrument_service(db: Session = Depends(get_db)):
    return FinancialInstrumentService(db)

def get_wallet_service(db: Session = Depends(get_db)):
    return DigitalWalletService(db)

def get_loan_use_cases(uow: UnitOfWork = Depends(get_uow)):
    return LoanUseCases(uow)


# --- Monitoring ---
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    # Check DB
    try:
        db.execute(sa.text("SELECT 1"))
        db_status = "up"
    except Exception:
        db_status = "down"
    
    return {
        "status": "ok" if db_status == "up" else "error",
        "services": {
            "database": db_status,
            "blockchain": "mock_active"
        }
    }

@app.get("/info")
def get_info():
    return {
        "app": "sblc-ledger-api",
        "version": "0.1.0",
        "environment": "development"
    }


@app.get("/public/verify/{reference}")
def public_verify_sblc(reference: str, db: Session = Depends(get_db)):
    sblc = db.execute(select(SBLC).where(SBLC.reference_number == reference)).scalar()
    if not sblc:
        raise HTTPException(status_code=404, detail="SBLC reference not found")
    
    # Return minimal safe data for public verification (No amounts or documents)
    return {
        "reference_number": sblc.reference_number,
        "status": str(sblc.status),
        "issuing_node": sblc.issuing_node.legal_name if sblc.issuing_node else "Institutional Participant",
        "expiry_date": sblc.expiry_date,
        "onchain_status": str(sblc.onchain_status),
        "tx_hash": sblc.tx_hash,
        "verified_at": datetime.now(timezone.utc)
    }


@app.post("/admin/invites")
def admin_invite_user(payload: dict, db: Session = Depends(get_db)):
    # Simple token generation
    token = secrets.token_urlsafe(32)
    new_invite = Invitation(
        email=payload['email'],
        role_name=payload['role_name'],
        ledger_id=payload['ledger_id'],
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(new_invite)
    db.commit()
    # In production, send email. For demo, we return the token
    return {"token": token, "invite_link": f"/onboarding?token={token}"}


@app.post("/auth/setup_password")
def setup_password(payload: dict, db: Session = Depends(get_db)):
    invite = db.execute(select(Invitation).where(Invitation.token == payload['token'], Invitation.is_used == False)).scalar()
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or used invitation token")
    
    # Create user
    hashed_pwd = get_password_hash(payload['password'])
    new_user = User(
        email=invite.email,
        full_name=invite.email.split('@')[0].capitalize(),
        hashed_password=hashed_pwd,
        is_active=True
    )
    db.add(new_user)
    
    # Assign Role
    role = db.execute(select(Role).where(Role.name == invite.role_name)).scalar()
    if role:
        user_role = UserLedgerRole(user_id=new_user.id, ledger_id=invite.ledger_id, role_id=role.id)
        db.add(user_role)
    
    invite.is_used = True
    db.commit()
    return {"status": "success", "message": "Account activated. Please login."}


# --- Auth ---
@app.post("/auth/register", response_model=UserOut)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(User).where(User.email == payload.email)).scalar()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        node_id=payload.node_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token)
async def login_for_access_token(
    request: Request, 
    db: Session = Depends(get_db), 
    redis: redis.Redis = Depends(get_redis),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = db.execute(select(User).where(User.email == form_data.username)).scalar()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Audit Login
    write_audit(
        db,
        event_type="auth.login",
        entity_type="user",
        entity_id=user.id,
        actor_user_id=user.id,
        actor_node_id=user.node_id,
        ip_address=request.client.host if request.client else None
    )
    db.commit() # Commit audit log
    
    return await create_tokens(str(user.id), redis)


@app.post("/auth/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = auth_header.split(" ")[1]
    try:
        import jwt
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti and exp:
            revocation = TokenRevocation(
                jti=UUID(jti),
                expires_at=datetime.fromtimestamp(exp, tz=timezone.utc)
            )
            db.merge(revocation)
            db.commit()
    except Exception:
        pass # If token is already invalid, no need to revoke

    return {"detail": "Successfully logged out"}


@app.post("/auth/refresh", response_model=Token)
async def refresh_token(
    request: Request, 
    redis: redis.Redis = Depends(get_redis)
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid refresh token")
    
    token = auth_header.split(" ")[1]
    return await refresh_access_token(token, redis)


@app.get("/auth/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# --- Ledgers ---
@app.post("/ledgers", response_model=LedgerOut)
def create_ledger(payload: LedgerCreate, db: Session = Depends(get_db)):
    ledger = LedgerRepository(db).create_ledger(name=payload.name, description=payload.description)
    db.commit()
    db.refresh(ledger)
    return ledger


@app.get("/ledgers", response_model=list[LedgerOut])
def list_ledgers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return LedgerRepository(db).list_ledgers(skip=skip, limit=limit)


@app.get("/ledgers/{ledger_id}", response_model=LedgerOut)
def get_ledger(ledger_id: str, db: Session = Depends(get_db)):
    from uuid import UUID

    ledger = LedgerRepository(db).get_ledger(UUID(ledger_id))
    if not ledger:
        raise HTTPException(status_code=404, detail="Ledger not found")
    return ledger


@app.delete("/ledgers/{ledger_id}", response_model=LedgerOut)
def delete_ledger(ledger_id: str, db: Session = Depends(get_db), actor: ActorInfo = Depends(require_permission("ledger.manage"))):
    from uuid import UUID
    ledger = LedgerRepository(db).delete_ledger(UUID(ledger_id))
    if not ledger:
        raise HTTPException(status_code=404, detail="Ledger not found")
    db.commit()
    return ledger


# --- Nodes ---
@app.post("/nodes", response_model=NodeOut)
def create_node(payload: NodeCreate, db: Session = Depends(get_db)):
    node = LedgerRepository(db).create_node(
        legal_name=payload.legal_name,
        display_name=payload.display_name,
        node_type=payload.node_type,
        country_code=payload.country_code,
        lei=payload.lei,
    )
    db.commit()
    db.refresh(node)
    return node


@app.get("/nodes", response_model=list[NodeOut])
def list_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return LedgerRepository(db).list_nodes(skip=skip, limit=limit)


@app.get("/nodes/{node_id}", response_model=NodeOut)
def get_node(node_id: str, db: Session = Depends(get_db)):
    from uuid import UUID

    node = LedgerRepository(db).get_node(UUID(node_id))
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@app.delete("/nodes/{node_id}", response_model=NodeOut)
def delete_node(node_id: str, db: Session = Depends(get_db), actor: ActorInfo = Depends(require_permission("node.manage"))):
    from uuid import UUID
    node = LedgerRepository(db).delete_node(UUID(node_id))
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    db.commit()
    return node


# --- Roles / Permissions ---
@app.get("/roles", response_model=list[RoleOut])
def list_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Roles and Permissions are handled by LedgerRepository for now (metadata)
    return LedgerRepository(db).session.scalars(select(Role).order_by(Role.name.asc()).offset(skip).limit(limit)).all()


@app.get("/permissions", response_model=list[PermissionOut])
def list_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return LedgerRepository(db).session.scalars(select(Permission).order_by(Permission.code.asc()).offset(skip).limit(limit)).all()


# --- Memberships ---
@app.post("/ledgers/{ledger_id}/memberships", response_model=MembershipOut)
def add_membership(ledger_id: str, payload: MembershipCreate, db: Session = Depends(get_db)):
    from uuid import UUID
    ledger_repo = LedgerRepository(db)

    # basic existence checks
    l_id = UUID(ledger_id)
    if not ledger_repo.get_ledger(l_id):
        raise HTTPException(status_code=404, detail="Ledger not found")
    if not ledger_repo.get_node(payload.node_id):
        raise HTTPException(status_code=404, detail="Node not found")

    # ensure role exists
    from app.domain.models import Role
    role = db.get(Role, payload.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    membership = ledger_repo.add_membership(
        ledger_id=l_id,
        node_id=payload.node_id,
        role_id=payload.role_id,
        status=payload.status,
    )
    db.commit()
    db.refresh(membership)
    return membership


@app.get("/ledgers/{ledger_id}/memberships", response_model=list[MembershipOut])
def list_memberships(ledger_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    from uuid import UUID

    return LedgerRepository(db).list_memberships(UUID(ledger_id), skip=skip, limit=limit)


# --- Audit ---
@app.get("/ledgers/{ledger_id}/audit", response_model=list[AuditOut])
def get_audit(ledger_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    from uuid import UUID

    return LedgerRepository(db).session.scalars(
        select(AuditEvent).where(AuditEvent.ledger_id == UUID(ledger_id))
        .order_by(AuditEvent.created_at.desc())
        .offset(skip).limit(limit)
    ).all()


# --- SBLCs ---
# --- Organizations ---
@app.post("/organizations", response_model=OrganizationOut)
def create_organization(
    payload: OrganizationCreate,
    uow: UnitOfWork = Depends(get_uow),
    actor: ActorInfo = Depends(require_permission("org.manage"))
):
    from app.domain.entities import Organization, OrganizationType
    from uuid import uuid4
    org = Organization(
        id=uuid4(),
        name=payload.name,
        org_type=OrganizationType(payload.org_type),
        country_code=payload.country_code
    )
    with uow:
        uow.organizations.save(org)
        uow.commit()
    return org

@app.get("/organizations", response_model=list[OrganizationOut])
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    uow: UnitOfWork = Depends(get_uow)
):
    return uow.organizations.list_all(skip=skip, limit=limit)

# --- Loans ---
@app.post("/loans", response_model=LoanOut)
async def create_loan(
    payload: LoanCreate,
    request: Request,
    use_cases: LoanUseCases = Depends(get_loan_use_cases),
    actor: ActorInfo = Depends(require_permission("loan.create"))
):
    return await use_cases.create_loan(
        actor_id=actor.user_id,
        organization_id=payload.organization_id,
        applicant_id=payload.applicant_id,
        beneficiary_id=payload.beneficiary_id,
        amount=payload.amount,
        currency=payload.currency,
        term_months=payload.term_months,
        interest_rate=payload.interest_rate,
        idempotency_key=payload.idempotency_key,
        ip_address=request.client.host if request.client else "unknown"
    )


@app.get("/ledgers/{ledger_id}/sblcs", response_model=list[SBLCOut])
async def list_sblcs(
    ledger_id: str, 
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    redis: redis.Redis = Depends(get_redis),
    actor: ActorInfo = Depends(require_permission("audit.read"))
):
    from uuid import UUID
    l_id = UUID(ledger_id)
    sblc_repo = SBLCRepository(db, redis)
    
    # Scoping logic
    applicant_node_id = None
    beneficiary_node_id = None
    
    if actor.role_name == "ApplicantUser":
        applicant_node_id = actor.node_id
    elif actor.role_name == "BeneficiaryUser":
        beneficiary_node_id = actor.node_id
        
    return await sblc_repo.list_by_ledger(
        l_id, 
        applicant_node_id=applicant_node_id, 
        beneficiary_node_id=beneficiary_node_id,
        skip=skip,
        limit=limit
    )


@app.get("/ledgers/{ledger_id}/sblcs/{sblc_id}", response_model=SBLCOut)
async def get_sblc(
    ledger_id: str, 
    sblc_id: str, 
    db: Session = Depends(get_db),
    redis: redis.Redis = Depends(get_redis),
    actor: ActorInfo = Depends(require_permission("audit.read"))
):
    from uuid import UUID
    sblc = await SBLCRepository(db, redis).get_by_id(UUID(sblc_id))
    if not sblc or str(sblc.ledger_id) != ledger_id:
        raise HTTPException(status_code=404, detail="SBLC not found in this ledger")
        
    # Detail scoping logic
    if actor.role_name == "ApplicantUser" and sblc.applicant_node_id != actor.node_id:
        raise HTTPException(status_code=403, detail="Detail access denied for this SBLC")
    if actor.role_name == "BeneficiaryUser" and sblc.beneficiary_node_id != actor.node_id:
        raise HTTPException(status_code=403, detail="Detail access denied for this SBLC")
        
    await manager.broadcast(json.dumps({
        "type": "SBLC_STATUS_CHANGE",
        "sblc_id": str(sblc.id),
        "reference_number": sblc.reference_number,
        "status": sblc.status
    }))
    return sblc


@app.delete("/ledgers/{ledger_id}/sblcs/{sblc_id}", response_model=SBLCOut)
async def delete_sblc(
    ledger_id: str, 
    sblc_id: str, 
    db: Session = Depends(get_db), 
    redis: redis.Redis = Depends(get_redis),
    actor: ActorInfo = Depends(require_permission("sblc.cancel"))
):
    from uuid import UUID
    sblc_repo = SBLCRepository(db, redis)
    sblc = await sblc_repo.get_by_id(UUID(sblc_id))
    if not sblc or str(sblc.ledger_id) != ledger_id:
        raise HTTPException(status_code=404, detail="SBLC not found in this ledger")
        
    deleted = await sblc_repo.delete(UUID(sblc_id))
    db.commit()
    return deleted


@app.post("/ledgers/{ledger_id}/sblcs/{sblc_id}/submit", response_model=SBLCOut)
async def submit_sblc(
    ledger_id: str, 
    sblc_id: str, 
    db: Session = Depends(get_db),
    redis: redis.Redis = Depends(get_redis),
    actor: ActorInfo = Depends(require_permission("sblc.create"))
):
    from uuid import UUID
    sblc = await transition_sblc_status(db, UUID(sblc_id), "submitted", redis)
    db.commit()
    db.refresh(sblc)
    
    await manager.broadcast(json.dumps({
        "type": "SBLC_STATUS_CHANGE",
        "sblc_id": str(sblc.id),
        "reference_number": sblc.reference_number,
        "status": sblc.status
    }))
    return sblc


@app.post("/ledgers/{ledger_id}/sblcs/{sblc_id}/request_review", response_model=ApprovalOut)
async def request_issuance_review(
    ledger_id: str, 
    sblc_id: str, 
    db: Session = Depends(get_db),
    redis: redis.Redis = Depends(get_redis),
    actor: ActorInfo = Depends(require_permission("sblc.review"))
):
    from uuid import UUID
    # This calls submit_for_approval which now does sovereignty check
    approval = await submit_for_approval(db, UUID(sblc_id), "issuance", actor.user_id, redis)
    db.commit()
    db.refresh(approval)
    return approval


@app.post("/loans/{loan_id}/approve", response_model=LoanOut)
async def approve_loan(
    loan_id: UUID,
    payload: ApprovalDecision,
    request: Request,
    use_cases: LoanUseCases = Depends(get_loan_use_cases),
    actor: ActorInfo = Depends(require_permission("loan.approve"))
):
    # Determine level from actor permissions or payload (simplified for now)
    level = 1 # In real system, extract from actor's role
    
    loan = await use_cases.approve_loan(
        actor_id=actor.user_id,
        loan_id=loan_id,
        level=level,
        decision=payload.status, # matches 'APPROVED' or 'REJECTED'
        comments=payload.comments,
        ip_address=request.client.host if request.client else "unknown"
    )
    
    await manager.broadcast(json.dumps({
        "type": "LOAN_STATUS_CHANGE",
        "loan_id": str(loan.id),
        "status": loan.status
    }))
    return loan


@app.post("/loans/{loan_id}/fund", response_model=LoanOut)
async def fund_loan(
    loan_id: UUID,
    request: Request,
    use_cases: LoanUseCases = Depends(get_loan_use_cases),
    actor: ActorInfo = Depends(require_permission("loan.fund"))
):
    return await use_cases.fund_loan(
        actor_id=actor.user_id,
        loan_id=loan_id,
        ip_address=request.client.host if request.client else "unknown"
    )

@app.post("/loans/{loan_id}/settle", response_model=LoanOut)
async def settle_loan(
    loan_id: UUID,
    request: Request,
    use_cases: LoanUseCases = Depends(get_loan_use_cases),
    actor: ActorInfo = Depends(require_permission("loan.settle"))
):
    return await use_cases.settle_loan(
        actor_id=actor.user_id,
        loan_id=loan_id,
        ip_address=request.client.host if request.client else "unknown"
    )


@app.post("/ledgers/{ledger_id}/sblcs/{sblc_id}/attachments", response_model=SBLCAttachmentOut)
async def upload_sblc_attachment(
    ledger_id: str,
    sblc_id: str,
    payload: SBLCAttachmentCreate,
    db: Session = Depends(get_db),
    actor: ActorInfo = Depends(require_permission("sblc.create"))
):
    from uuid import UUID
    import hashlib
    
    # In a real system, we'd handle the file upload here.
    # For this controlled reference system, we accept the metadata and hash.
    # We log it as an auditable reference.
    
    attachment = crud.create_sblc_attachment(
        db,
        sblc_id=UUID(sblc_id),
        filename=payload.filename,
        file_type=payload.file_type,
        file_hash=payload.file_hash,
        visibility=payload.visibility
    )
    db.commit()
    db.refresh(attachment)
    return attachment


# --- Claims ---


@app.get("/ledgers/{ledger_id}/sblcs/{sblc_id}/claims", response_model=list[ClaimOut])
def list_claims(
    ledger_id: str, 
    sblc_id: str, 
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    actor_id: ActorInfo = Depends(require_permission("audit.read"))
):
    from uuid import UUID
    # Basic existence check
    sblc = crud.get_sblc(db, UUID(sblc_id))
    if not sblc or str(sblc.ledger_id) != ledger_id:
        raise HTTPException(status_code=404, detail="SBLC not found in this ledger")
        
    return crud.list_claims(db, UUID(sblc_id), skip=skip, limit=limit)


@app.delete("/ledgers/{ledger_id}/sblcs/{sblc_id}/claims/{claim_id}", response_model=ClaimOut)
def delete_claim(
    ledger_id: str, 
    sblc_id: str, 
    claim_id: str, 
    db: Session = Depends(get_db), 
    actor: ActorInfo = Depends(require_permission("claim.review")) 
):
    from uuid import UUID
    claim = crud.get_claim(db, UUID(claim_id))
    if not claim or str(claim.sblc_id) != sblc_id:
         raise HTTPException(status_code=404, detail="Claim not found for this SBLC")

    deleted = crud.delete_claim(db, UUID(claim_id))
    db.commit()
    return deleted


# --- Phase 4: Advanced Workflows ---

@app.post("/ledgers/{ledger_id}/sblcs/{sblc_id}/request_issuance", response_model=ApprovalOut)
async def request_issuance(
    ledger_id: str, 
    sblc_id: str, 
    db: Session = Depends(get_db), 
    redis: redis.Redis = Depends(get_redis),
    actor: ActorInfo = Depends(require_permission("sblc.issue"))
):
    from uuid import UUID
    # Verify ledger ownership
    sblc = await SBLCRepository(db, redis).get_by_id(UUID(sblc_id))
    if not sblc or str(sblc.ledger_id) != ledger_id: raise HTTPException(status_code=404, detail="SBLC not found")

    approval = await submit_for_approval(db, UUID(sblc_id), "issuance", actor.user_id, redis)
    db.commit()
    db.refresh(approval)
    return approval


# ...

@app.post("/approvals/{approval_id}/process", response_model=ApprovalOut)
async def process_approval_endpoint(
    approval_id: str,
    request: Request,
    db: Session = Depends(get_db),
    redis: redis.Redis = Depends(get_redis),
    actor: ActorInfo = Depends(require_permission("sblc.approve"))
):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    print(f"DEBUG BODY: {payload}")
    from uuid import UUID
    # Validation manually
    if "decision" not in payload:
        raise HTTPException(status_code=422, detail="Missing decision")
    
    print(f"Processing Approval: {approval_id} with decision: {payload['decision']}")
    # process_approval now handles sovereignty check
    approval = await process_approval(db, UUID(approval_id), payload["decision"], actor.user_id, payload.get("comments"), redis)
    db.commit()
    db.refresh(approval)
    return approval


@app.post("/ledgers/{ledger_id}/sblcs/{sblc_id}/amendments", response_model=SBLCAmendmentOut)
def create_amendment_request(
    ledger_id: str,
    sblc_id: str,
    payload: SBLCAmendmentCreate,
    db: Session = Depends(get_db),
    actor: ActorInfo = Depends(require_permission("sblc.amend"))
):
    from uuid import UUID
    sblc = crud.get_sblc(db, UUID(sblc_id))
    if not sblc or str(sblc.ledger_id) != ledger_id: raise HTTPException(status_code=404, detail="SBLC not found")

    # 1. Start amendment workflow
    submit_for_approval(db, UUID(sblc_id), "amendment", actor.user_id)
    
    # 2. Create amendment record
    amendment = crud.create_amendment(
        db, 
        sblc_id=UUID(sblc_id), 
        change_description=payload.change_description, 
        new_values=payload.new_values,
        status="pending"
    )
    db.commit()
    db.refresh(amendment)
    return amendment


@app.get("/ledgers/{ledger_id}/sblcs/{sblc_id}/approvals", response_model=list[ApprovalOut])
def list_approvals(
    ledger_id: str,
    sblc_id: str,
    db: Session = Depends(get_db),
    actor: ActorInfo = Depends(require_permission("audit.read"))
):
    from uuid import UUID
    sblc = crud.get_sblc(db, UUID(sblc_id))
    if not sblc or str(sblc.ledger_id) != ledger_id: raise HTTPException(status_code=404, detail="SBLC not found")

    return crud.list_approvals(db, UUID(sblc_id))


@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/analytics/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    from sqlalchemy import func
    
    # Status distribution
    status_counts = db.query(SBLC.status, func.count(SBLC.id)).group_by(SBLC.status).all()
    status_data = [{"status": s.value if hasattr(s, 'value') else s, "count": c} for s, c in status_counts]
    
    # Volume by currency
    volume = db.query(SBLC.currency, func.sum(SBLC.amount)).group_by(SBLC.currency).all()
    volume_data = [{"currency": curr, "total": float(vol) if vol else 0} for curr, vol in volume]
    
    # Recent activity for line chart
    recent_sblcs = db.query(SBLC.created_at, SBLC.amount).order_by(SBLC.created_at.desc()).limit(20).all()
    activity_data = [{"date": s.created_at.isoformat(), "amount": float(s.amount)} for s in recent_sblcs]
    
    return {
        "status_distribution": status_data,
        "volume_by_currency": volume_data,
        "recent_activity": activity_data
    }
@app.get("/compliance/reports/sblc-summary")
async def get_compliance_sblc_report(
    region: Optional[str] = None,
    db: Session = Depends(get_db),
    actor: ActorInfo = Depends(require_permission("audit.read"))
):
    """
    Generates a system-wide or region-specific compliance report.
    """
    from app.application.services.compliance_service import ComplianceService
    
    # Auditing the report access
    from app.infrastructure.audit import write_audit
    write_audit(
        db,
        event_type="compliance.report_generated",
        entity_type="system",
        entity_id=actor.user_id, # Link to actor for traceability
        actor_user_id=actor.user_id,
        after={"region_filter": region}
    )
    
    return ComplianceService(db).generate_sblc_report(region_id=region)

# --- Institutional Banking & Compliance Endpoints ---

@app.get("/banking/external-banks", response_model=List[OrganizationOut])
def list_external_banks(uow: UnitOfWork = Depends(get_uow)):
    # Organizations marked as 'bank'
    from app.domain.entities import OrganizationType
    return uow.organizations.list_all(skip=0, limit=100) # Simplified: returns all orgs for now

@app.post("/banking/accounts", response_model=AccountOut)
def create_institution_account(
    payload: AccountCreate, 
    service: BankingService = Depends(get_banking_service),
    actor: ActorInfo = Depends(require_permission("org.manage"))
):
    return service.create_account(
        node_id=payload.node_id,
        account_number=payload.account_number,
        currency=payload.currency,
        account_type=payload.account_type,
        parent_id=payload.parent_id,
        is_nostro=payload.is_nostro
    )

@app.get("/banking/accounts", response_model=List[AccountOut])
def list_institution_accounts(
    node_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    from app.domain.models import InstitutionAccount
    query = select(InstitutionAccount)
    if node_id:
        query = query.where(InstitutionAccount.node_id == node_id)
    return db.scalars(query).all()

@app.post("/banking/transfers", response_model=WireTransferOut)
def initiate_transfer(
    payload: WireTransferCreate,
    service: BankingService = Depends(get_banking_service),
    compliance: ComplianceService = Depends(get_compliance_service),
    actor: ActorInfo = Depends(require_permission("loan.create")) # Using existing permission for now
):
    # 1. Initiate transfer
    tx = service.initiate_wire_transfer(
        sender_id=payload.sender_account_id,
        receiver_id=payload.receiver_account_id,
        amount=payload.amount,
        currency=payload.currency,
        reference=payload.reference
    )
    
    # 2. Run initial compliance check
    compliance.check_transaction(tx.id)
    
    return tx

@app.post("/banking/transfers/{tx_id}/confirm", response_model=WireTransferOut)
def confirm_transfer(
    tx_id: UUID,
    service: BankingService = Depends(get_banking_service),
    actor: ActorInfo = Depends(require_permission("loan.approve"))
):
    service.confirm_transfer(tx_id)
    return service.db.get(WireTransaction, tx_id)

@app.get("/compliance/cb-portal/{country_code}", response_model=CBPortalQueryOut)
def query_central_bank_portal(
    country_code: str,
    account_number: str,
    service: ComplianceService = Depends(get_compliance_service)
):
    return service.query_cb_portal(country_code, account_number)

@app.get("/banking/seed-data")
def seed_banking_data(service: BankingService = Depends(get_banking_service)):
    service.seed_external_banks()
    return {"status": "success", "message": "External banks seeded"}


# --- Financial Instruments ---

@app.post("/banking/instruments", response_model=InstrumentOut)
def issue_instrument(
    payload: InstrumentCreate,
    service: FinancialInstrumentService = Depends(get_instrument_service),
    actor: ActorInfo = Depends(require_permission("loan.create"))
):
    return service.issue_instrument(
        name=payload.name,
        instrument_type=payload.instrument_type,
        issuer_node_id=payload.issuer_node_id,
        par_value=payload.par_value,
        currency=payload.currency,
        isin=payload.isin,
        maturity_date=payload.maturity_date,
        coupon_rate=payload.coupon_rate,
        is_national_debt=payload.is_national_debt,
        metadata_json=payload.metadata_json
    )

@app.get("/banking/instruments", response_model=List[InstrumentOut])
def list_instruments(
    issuer_id: Optional[UUID] = None,
    service: FinancialInstrumentService = Depends(get_instrument_service)
):
    return service.get_instruments(issuer_id=issuer_id)


# --- Digital Wallets ---

@app.post("/banking/wallets", response_model=WalletOut)
def register_wallet(
    payload: WalletCreate,
    service: DigitalWalletService = Depends(get_wallet_service),
    actor: ActorInfo = Depends(require_permission("org.manage"))
):
    return service.register_wallet(
        node_id=payload.node_id,
        wallet_type=payload.wallet_type,
        address=payload.address,
        metadata_json=payload.metadata_json
    )

@app.get("/banking/wallets", response_model=List[WalletOut])
def list_wallets(
    node_id: Optional[UUID] = None,
    service: DigitalWalletService = Depends(get_wallet_service)
):
    if node_id:
        return service.get_wallets_for_node(node_id)
    return service.list_all_wallets()

@app.post("/banking/wallets/{wallet_id}/verify", response_model=WalletOut)
def verify_wallet(
    wallet_id: UUID,
    payload: WalletVerifyPayload,
    service: DigitalWalletService = Depends(get_wallet_service),
    actor: ActorInfo = Depends(require_permission("loan.approve"))
):
    return service.verify_wallet(wallet_id, payload.verifying_bank_id)
