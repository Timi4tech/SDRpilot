# src/infrastructure/web/security/auth.py
import os
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
import jwt

from src.infrastructure.config.redis_config import redis_service

logger = logging.getLogger(__name__)

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
SESSION_TIMEOUT_SECONDS = 15 * 60  # 15 minutes

PUBLIC_PATHS = {"/", "/docs", "/openapi.json", "/health", "/login"}


SESSION_PREFIX = os.environ["SESSION_PREFIX"] 
REVOKED_PREFIX = os.environ["REVOKED_PREFIX"]  


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_prefix: str = "/protected"):
        super().__init__(app)
        self.protected_prefix = protected_prefix

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        if path in PUBLIC_PATHS or not path.startswith(self.protected_prefix):
            return await call_next(request)

        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Missing or malformed Authorization header"},
                status_code=401,
            )

        token = auth_header.split(" ", 1)[1]

        try:
            
            if await redis_service.client.get(f"{REVOKED_PREFIX}{token}"):
                return JSONResponse(
                    {"detail": "Session expired. Please log in again."},
                    status_code=401,
                )
        except Exception:
            logger.error("Redis unavailable during revocation check", exc_info=True)
            return JSONResponse(
                {"detail": "Could not verify session. Please retry."},
                status_code=503,
            )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return JSONResponse({"detail": "Token expired"}, status_code=401)
        except jwt.InvalidTokenError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        session_key = f"{SESSION_PREFIX}{token}"

        try:
            session_exists = await redis_service.client.exists(session_key)
        except Exception:
            logger.error("Redis unavailable during session check", exc_info=True)
            return JSONResponse(
                {"detail": "Could not verify session. Please retry."},
                status_code=503,
            )

        if not session_exists:
            return JSONResponse(
                {"detail": "Session expired due to inactivity. Please log in again."},
                status_code=401,
            )

        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse({"detail": "Invalid token payload"}, status_code=401)

        request.state.current_user = user_id

        
        try:
            await redis_service.client.setex(session_key, SESSION_TIMEOUT_SECONDS, user_id)
        except Exception:
            logger.error("Redis unavailable while refreshing session TTL", exc_info=True)
            pass

        return await call_next(request)