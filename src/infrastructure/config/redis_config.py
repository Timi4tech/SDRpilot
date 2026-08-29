import os
import logging
from upstash_redis.asyncio import Redis  

logger = logging.getLogger(__name__)


class UpstashRedisService:
    def __init__(self):
        self.url = os.getenv("UPSTASH_REDIS_REST_URL")
        self.token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        self.client: Redis | None = None

    def connect(self) -> None:
        """Initializes the connectionless HTTP client."""
        if not self.url or not self.token:
            raise RuntimeError("Missing Upstash configuration environment credentials.")

        self.client = Redis(url=self.url, token=self.token)
        logger.info("Upstash Redis client initialized.")

    async def verify_connection(self) -> bool:
        """Call on app startup to fail fast if Upstash is unreachable —
        mirrors verify_connection() in persistence/db.py."""
        if not self.client:
            raise RuntimeError("Redis client not initialized — call connect() first.")

        try:
            await self.client.ping()
            logger.info("Upstash Redis connection verified.")
            return True
        except Exception:
            logger.error("Upstash Redis connection failed.", exc_info=True)
            raise

    async def close(self) -> None:
        """Closes the underlying aiohttp session securely."""
        if self.client:
            try:
                await self.client.close()
            except Exception:
                logger.warning("Error while closing Redis client.", exc_info=True)
            finally:
                self.client = None



redis_service = UpstashRedisService()