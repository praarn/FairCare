"""User accounts, server-side sessions, and password-reset tokens.

Now backed by Postgres (``users`` / ``auth_sessions`` / ``password_reset_tokens``)
instead of JSON files. Password hashing is unchanged: stdlib PBKDF2-HMAC-SHA256,
random 16-byte salt per user, no external crypto dependency.
"""
import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import AuthSession, PasswordResetToken, User


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _aware(dt: datetime) -> datetime:
    """SQLite round-trips datetimes as naive; normalise before comparing."""
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


# ---------- password hashing (stdlib only) ----------

def hash_password(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    salt_hex = salt_hex or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        settings.pbkdf2_iterations,
    )
    return digest.hex(), salt_hex


def _verify_password(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    digest, _ = hash_password(password, salt_hex)
    return secrets.compare_digest(digest, expected_hash_hex)


def _public_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": bool(user.is_admin),
    }


# ---------- public API used by the router ----------

def create_user(db: Session, name: str, email: str, password: str) -> dict:
    email = email.strip().lower()
    exists = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if exists:
        raise ValueError("An account with this email already exists.")

    password_hash, salt = hash_password(password)
    user = User(
        id=secrets.token_hex(8),
        name=name.strip(),
        email=email,
        password_hash=password_hash,
        password_salt=salt,
        created_at=_utcnow(),
    )
    db.add(user)
    db.commit()
    return _public_user(user)


def authenticate_user(db: Session, email: str, password: str) -> dict | None:
    email = email.strip().lower()
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        return None
    if _verify_password(password, user.password_salt, user.password_hash):
        return _public_user(user)
    return None


def create_session(db: Session, email: str) -> str:
    token = secrets.token_urlsafe(32)
    db.add(
        AuthSession(
            token=token,
            email=email.strip().lower(),
            expires_at=_utcnow() + timedelta(seconds=settings.session_ttl_seconds),
        )
    )
    db.commit()
    return token


def get_user_by_session(db: Session, token: str) -> dict | None:
    session = db.get(AuthSession, token)
    if not session or _aware(session.expires_at) < _utcnow():
        return None
    user = db.execute(
        select(User).where(User.email == session.email)
    ).scalar_one_or_none()
    return _public_user(user) if user else None


def delete_session(db: Session, token: str) -> None:
    session = db.get(AuthSession, token)
    if session:
        db.delete(session)
        db.commit()


def create_reset_token(db: Session, email: str) -> str | None:
    """Returns None if no account exists for this email (caller decides whether
    to reveal that, to avoid leaking which emails are registered)."""
    email = email.strip().lower()
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        return None

    token = secrets.token_urlsafe(24)
    db.add(
        PasswordResetToken(
            token=token,
            email=email,
            expires_at=_utcnow() + timedelta(seconds=settings.reset_token_ttl_seconds),
        )
    )
    db.commit()
    return token


def reset_password(db: Session, token: str, new_password: str) -> bool:
    entry = db.get(PasswordResetToken, token)
    if not entry or _aware(entry.expires_at) < _utcnow():
        return False

    user = db.execute(
        select(User).where(User.email == entry.email)
    ).scalar_one_or_none()
    if not user:
        return False

    user.password_hash, user.password_salt = hash_password(new_password)
    db.delete(entry)
    db.commit()
    return True
