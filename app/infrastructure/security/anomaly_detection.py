from fastapi import Request, HTTPException
import redis.asyncio as redis
from starlette.middleware.base import BaseHTTPMiddleware
import json

class AnomalyDetectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis = redis_client

    async def dispatch(self, request: Request, call_next):
        # Only check for authenticated requests (simplified)
        # In real system, wait for auth middleware to populate request.state.user
        user_id = request.headers.get("X-User-ID") # Mock extraction
        if user_id:
            current_ip = request.client.host if request.client else "unknown"
            last_ip = await self.redis.get(f"last_ip:{user_id}")
            
            if last_ip and last_ip.decode() != current_ip:
                # Log anomaly
                print(f"ANOMALY: User {user_id} changed IP from {last_ip.decode()} to {current_ip}")
                # We could block or force MFA here. For this phase, we just log.
            
            await self.redis.setex(f"last_ip:{user_id}", 3600, current_ip)

        response = await call_next(request)
        return response
