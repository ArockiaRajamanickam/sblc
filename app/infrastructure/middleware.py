import time
import uuid
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# --- Simple In-Memory Rate Limiter ---
class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.limit = requests_limit
        self.window = window_seconds
        self.history = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        # Clean old records
        self.history[client_ip] = [t for t in self.history[client_ip] if now - t < self.window]
        
        if len(self.history[client_ip]) >= self.limit:
            return False
            
        self.history[client_ip].append(now)
        return True

# Initialize limiters
auth_limiter = RateLimiter(requests_limit=5, window_seconds=60) # 5 requests per minute

# --- Middlewares ---

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

async def rate_limit_auth(request: Request, call_next):
    if request.url.path in ["/auth/login", "/auth/register"]:
        ip = request.client.host if request.client else "unknown"
        if not auth_limiter.is_allowed(ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )
    return await call_next(request)
