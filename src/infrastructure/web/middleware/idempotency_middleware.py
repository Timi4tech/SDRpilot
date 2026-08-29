# src/infrastructure/web/security/idempotency.py
import json
import logging
from fastapi import Request, HTTPException, status
from src.infrastructure.config.redis_config import redis_service

logger = logging.getLogger(__name__)


class IdempotencyReplay(Exception):
    """Raised when a previously-completed response should be replayed verbatim."""
    def __init__(self, status_code: int, body: dict):
        self.status_code = status_code
        self.body = body


class IdempotencyManager:
    @staticmethod
    async def verify_key(request: Request) -> str | None:
        """Reads and reserves the idempotency key prior to request processing."""
        if request.method not in ["POST", "PUT", "PATCH"]:
            return None

        idempotency_key = request.headers.get("X-Idempotency-Key")
        if not idempotency_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required 'X-Idempotency-Key' header for this mutating action."
            )

        redis_key = f"idempotency:{idempotency_key}"

        
        try:
            is_new_request = await redis_service.client.set(redis_key, "in_flight", ex=3600, nx=True)
        except Exception:
            logger.error("Redis unavailable during idempotency check for %s", redis_key, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not verify request uniqueness. Please retry."
            )

        if is_new_request:
            return redis_key

        try:
            current_value = await redis_service.client.get(redis_key)
        except Exception:
            logger.error("Redis unavailable reading idempotency key %s", redis_key, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not verify request uniqueness. Please retry."
            )

        if current_value is None:
        
            return redis_key

        if current_value == "in_flight":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A duplicate request with this exact key is currently processing. Please wait."
            )

        try:
            cached_response = json.loads(current_value)
        except json.JSONDecodeError:
            logger.error("Corrupt idempotency record for %s", redis_key)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Idempotency record corrupted."
            )

        raise IdempotencyReplay(
            status_code=cached_response["status_code"],
            body=cached_response["body"],
        )

    @staticmethod
    async def save_response(redis_key: str | None, response_data, status_code: int = 201) -> None:
        """Saves the completed execution payload over the 'in_flight' token."""
        if not redis_key:
            return

        serializable_body = _to_serializable(response_data)
        payload = {
            "status_code": status_code,
            "body": serializable_body,
        }

        try:
            await redis_service.client.set(redis_key, json.dumps(payload), ex=86400)
        except Exception:

            logger.error("Failed to save idempotency record for %s", redis_key, exc_info=True)


def _to_serializable(result):
    """Convert Pydantic models / dataclasses / nested structures into plain JSON-safe data."""
    if hasattr(result, "model_dump"):      
        return result.model_dump(mode="json")
    if hasattr(result, "dict"):            
        return result.dict()
    if isinstance(result, (list, tuple)):
        return [_to_serializable(item) for item in result]
    return result