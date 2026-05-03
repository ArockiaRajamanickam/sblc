import redis.asyncio as redis
from typing import Optional
from app.infrastructure.db import settings

class RedisManager:
    """
    Manages Redis connections for caching and session state.
    Used for Token Blacklisting and Refresh Token Rotation tracking.
    """
    def __init__(self, redis_url: str):
         self.redis_url = redis_url
         self._client: Optional[redis.Redis] = None

    async def get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = await redis.from_url(
                self.redis_url, 
                encoding="utf-8", 
                decode_responses=True
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None

# Default instance (initialized with URL from settings)
# Note: Add REDIS_URL to settings if not present
redis_url = getattr(settings, "redis_url", "redis://localhost:6379/0")
redis_manager = RedisManager(redis_url)

async def get_redis():
    return await redis_manager.get_client()

def get_redis_sync():
    import redis
    return redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
