"""Publica limites RPM por API key no Redis (consumido pelo RateLimiter)."""
from __future__ import annotations

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


async def set_api_key_rpm(key_hash: str, rpm: int) -> None:
    try:
        import redis.asyncio as redis

        client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        try:
            await client.set(f"apikey:rpm:{key_hash}", str(max(1, int(rpm))))
        finally:
            await client.aclose()
    except Exception as exc:
        logger.debug("Redis apikey rpm não gravado: %s", exc)


async def delete_api_key_rpm(key_hash: str) -> None:
    try:
        import redis.asyncio as redis

        client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        try:
            await client.delete(f"apikey:rpm:{key_hash}")
        finally:
            await client.aclose()
    except Exception as exc:
        logger.debug("Redis apikey rpm não removido: %s", exc)
