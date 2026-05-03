from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4
import jwt
from app.infrastructure.db import settings
import redis.asyncio as redis

class JWTHandler:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def create_tokens(self, user_id: str) -> dict:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=7)
        
        jti = str(uuid4())
        access_payload = {
            "sub": user_id,
            "jti": jti,
            "exp": datetime.utcnow() + access_token_expires,
            "iat": datetime.utcnow()
        }
        access_token = jwt.encode(access_payload, settings.secret_key, algorithm=settings.algorithm)
        
        refresh_jti = str(uuid4())
        refresh_payload = {
            "sub": user_id,
            "jti": refresh_jti,
            "exp": datetime.utcnow() + refresh_token_expires,
            "iat": datetime.utcnow()
        }
        refresh_token = jwt.encode(refresh_payload, settings.secret_key, algorithm=settings.algorithm)
        
        # Store refresh token in Redis for rotation
        await self.redis.setex(f"refresh:{refresh_jti}", int(refresh_token_expires.total_seconds()), user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def revoke_token(self, jti: str, expires_in_seconds: int):
        await self.redis.setex(f"revoked:{jti}", expires_in_seconds, "true")

    async def is_revoked(self, jti: str) -> bool:
        return await self.redis.exists(f"revoked:{jti}")
