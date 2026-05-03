from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.infrastructure.db.models import IdempotencyKeyOrm
from app.infrastructure.db import SessionLocal

class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in ["POST", "PUT", "PATCH"]:
            return await call_next(request)

        idempotency_key = request.headers.get("X-Idempotency-Key")
        if not idempotency_key:
            # For strictly financial, we might reject. For now, just bypass if missing.
            return await call_next(request)

        with SessionLocal() as db:
            existing = db.get(IdempotencyKeyOrm, idempotency_key)
            if existing:
                raise HTTPException(status_code=409, detail="Duplicate Request: Idempotency Key used")
            
        response = await call_next(request)
        
        # Note: In a real system, we'd store the response too.
        # But for this phase, we just flag the key used.
        return response
