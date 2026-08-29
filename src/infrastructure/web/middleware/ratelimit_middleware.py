# src/infrastructure/web/security/rate_limiter.py
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from src.infrastructure.config.redis_config import redis_service

logger = logging.getLogger(__name__)


ESCALATION_TIERS = [
    (5 * 60, 5),    
    (15 * 60, 7),   
    (60 * 60, 10),  
]

INITIAL_BUCKET_TOKENS = 10


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_limit: int = INITIAL_BUCKET_TOKENS, protected_prefix: str = "/"):
        super().__init__(app)
        self.limit = requests_limit
        self.protected_prefix = protected_prefix

    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.url.path.startswith(self.protected_prefix):
            return await call_next(request)

        user_id = getattr(request.state, "current_user", None) or request.client.host
        bucket_key = f"rate_limit:bucket:{request.url.path}:{user_id}"
        lockout_key = f"rate_limit:lockout:{request.url.path}:{user_id}"
        violation_key = f"rate_limit:violations:{request.url.path}:{user_id}"

        try:
            
            lockout_ttl = await redis_service.client.ttl(lockout_key)
            if lockout_ttl and lockout_ttl > 0:
                return self._too_many_requests(lockout_ttl)

            
            bucket_exists = await redis_service.client.exists(bucket_key)
            if not bucket_exists:
                await redis_service.client.set(bucket_key, INITIAL_BUCKET_TOKENS)

            
            remaining = await redis_service.client.decr(bucket_key)

            if remaining >= 0:
                return await call_next(request)  

            
            violation_count = await redis_service.client.incr(violation_key)
            
            await redis_service.client.expire(violation_key, 24 * 60 * 60)

            tier_index = min(violation_count - 1, len(ESCALATION_TIERS) - 1)
            lockout_seconds, refill_tokens = ESCALATION_TIERS[tier_index]

            
            await redis_service.client.set(lockout_key, "locked", ex=lockout_seconds)

         
            await redis_service.client.set(bucket_key, refill_tokens, ex=lockout_seconds)

            if lockout_seconds == 15 * 60:
                logger.warning(
                    "RATE LIMIT ALERT: user=%s path=%s hit 15-minute escalation tier "
                    "(violation #%d)",
                    user_id, request.url.path, violation_count
                )

            return self._too_many_requests(lockout_seconds)

        except Exception:
            logger.error("Redis unavailable during rate limit check for %s", bucket_key, exc_info=True)
            return await call_next(request)

    def _too_many_requests(self, seconds: int) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"detail": f"Rate limit exceeded. Please try again in {self._format_time(seconds)}."},
            headers={"Retry-After": str(seconds)}
        )

    @staticmethod
    def _format_time(seconds: int) -> str:
        if seconds < 60:
            return f"{seconds} seconds"
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"