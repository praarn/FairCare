"""Shared slowapi limiter.

In-memory storage by default (fine for a single process / demo). Point
``RATE_LIMIT_STORAGE_URI`` at Redis later for multi-worker deployments.
"""
import os

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# headers_enabled stays False: slowapi's per-route header injection requires the
# handler to return a starlette Response, but ours return dicts / Pydantic models.
# Rate limiting itself (the 429) works regardless.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
    storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://"),
    headers_enabled=False,
)
