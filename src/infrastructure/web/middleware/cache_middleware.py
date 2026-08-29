# src/infrastructure/cache/cache_decorator.py
import json
import functools
import logging
from fastapi import Request
from src.infrastructure.config.redis_config import redis_service

logger = logging.getLogger(__name__)


def cache_response(expire_seconds: int = 300):
    """Caches an endpoint response based on its function arguments."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request | None = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request is None:
                return await func(*args, **kwargs)

            cache_key = f"cache:{request.url.path}:{request.url.query}"
            try:
                cached_data = await redis_service.client.get(cache_key)
            except Exception:
                logger.warning("Cache read failed for %s", cache_key, exc_info=True)
                cached_data = None

            if cached_data:
                try:
                    return json.loads(cached_data)
                except json.JSONDecodeError:
                    logger.warning("Corrupt cache entry for %s, ignoring", cache_key)

            result = await func(*args, **kwargs)

          
            try:
                serializable_result = _to_serializable(result)
                payload = json.dumps(serializable_result)
            except (TypeError, ValueError):
                logger.warning("Result for %s is not JSON-serializable, skipping cache write", cache_key)
                return result

            
            try:
                await redis_service.client.set(cache_key, payload, ex=expire_seconds)
            except Exception:
                logger.warning("Cache write failed for %s", cache_key, exc_info=True)

            return result
        return wrapper
    return decorator


def _to_serializable(result):
    """Convert Pydantic models / dataclasses / nested structures into plain JSON-safe data."""
    if hasattr(result, "model_dump"):       
        return result.model_dump(mode="json")
    if hasattr(result, "dict"):            
        return result.dict()
    if isinstance(result, (list, tuple)):
        return [_to_serializable(item) for item in result]
    return result