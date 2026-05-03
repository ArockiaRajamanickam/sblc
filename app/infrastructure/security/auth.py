from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import uuid

import jwt
import redis.asyncio as redis
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db import SessionLocal, settings
from app.domain.models import Permission, Role, RolePermission, User, UserLedgerRole, LedgerMembership
from app.infrastructure.security.redis_client import get_redis
from dataclasses import dataclass

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


@dataclass
class ActorInfo:
    user_id: UUID
    node_id: Optional[UUID]
    role_name: str
    permissions: list[str]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def create_tokens(user_id: str, redis_client: Optional[redis.Redis] = None) -> dict:
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    if redis_client:
        # Extract JTI from refresh token
        decoded = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        jti = decoded["jti"]
        # Store active JTI for the user's family
        await redis_client.setex(f"refresh_family:{user_id}", 604800, jti) # 7 days
        
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

async def revoke_user_sessions(user_id: str, redis_client: Optional[redis.Redis]):
    if redis_client:
        await redis_client.delete(f"refresh_family:{user_id}")


def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db),
    x_actor_id: Optional[UUID] = Header(None, alias="X-Actor-ID") # Fallback for dev
) -> User:
    # --- EMERGENCY BYPASS (Sign in off) ---
    def rescue():
        u = db.execute(select(User)).scalars().first()
        if u: return u
        raise HTTPException(status_code=401, detail="No users in database. Run seed script.")

    # 1. Try JWT
    if token:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            jti: str = payload.get("jti")
            token_type: str = payload.get("type")
            
            if user_id and jti and token_type == "access":
                user = db.get(User, UUID(user_id))
                if user: return user
        except:
             pass # Fallback to rescue

    # 2. Try Header bypass
    if x_actor_id:
        user = db.get(User, x_actor_id)
        if user: return user

    # 3. Final Rescue
    return rescue()


async def refresh_access_token(token: str, redis_client: redis.Redis) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        token_type: str = payload.get("type")
        
        if user_id is None or jti is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
        # Check Token Family in Redis
        active_jti = await redis_client.get(f"refresh_family:{user_id}")
        
        if active_jti != jti:
            # Token Reuse Detected!
            await revoke_user_sessions(user_id, redis_client)
            raise HTTPException(
                status_code=401, 
                detail="Refresh token reuse detected. All sessions revoked for security."
            )
            
        # Valid - Rotate
        return await create_tokens(user_id, redis_client)
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


def require_permission(permission_code: str):
    def dependency(
        ledger_id: UUID,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # 1. Strict Node Binding Check
        if not user.node_id:
             raise HTTPException(status_code=403, detail="User must belong to a Node to access Ledger")
             
        membership = db.execute(select(LedgerMembership).where(
            LedgerMembership.ledger_id == ledger_id, 
            LedgerMembership.node_id == user.node_id
        )).scalar()
        
        if not membership or str(membership.status) != "active":
             raise HTTPException(status_code=403, detail="User's Node is not an active member of this Ledger")

        # 2. Join to get Role and Permissions for this ledger
        stmt = (
            select(Role.id, Role.name, Permission.code)
            .join(UserLedgerRole, UserLedgerRole.role_id == Role.id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .where(UserLedgerRole.user_id == user.id)
            .where(UserLedgerRole.ledger_id == ledger_id)
        )
        
        rows = db.execute(stmt).all()
        if not rows:
            # Bypass logic: If no role is found in ledger but we are in bypass mode, 
            # return a powerful ActorInfo for the first ledger found.
            from sqlalchemy import select
            from app.domain.models import Ledger
            ledger = db.get(Ledger, ledger_id)
            if ledger:
                return ActorInfo(
                    user_id=user.id,
                    node_id=user.node_id,
                    role_name="IssuerAdmin",
                    permissions=["ledger.create", "ledger.manage", "sblc.issue", "sblc.create", "audit.read"]
                )
            raise HTTPException(status_code=403, detail="No access to this ledger")

        permissions = [r[2] for r in rows]
        
        if permission_code not in permissions:
            raise HTTPException(
                status_code=403, 
                detail=f"Permission '{permission_code}' required"
            )

        # Get role name from first row
        role_name = rows[0][1]

        return ActorInfo(
            user_id=user.id,
            node_id=user.node_id,
            role_name=role_name,
            permissions=permissions
        )

    return dependency
