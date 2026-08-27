"""Shared FastAPI dependencies for routes that need an authenticated user.

Mirrors the header handling in ``routers/auth.py`` but returns the public user
dict (now including ``is_admin``) so downstream routes can authorise.
"""

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import auth_service


def _token_from_header(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )
    return authorization.split(" ", 1)[1]


def current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    token = _token_from_header(authorization)
    user = auth_service.get_user_by_session(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    return user


def current_admin(
    user: dict = Depends(current_user),
) -> dict:
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user


def optional_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict | None:
    """Like ``current_user`` but returns ``None`` instead of raising when there
    is no valid session — for routes that work anonymously but attribute the
    action to a user when one is signed in."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    user = auth_service.get_user_by_session(db, authorization.split(" ", 1)[1])
    return user or None
