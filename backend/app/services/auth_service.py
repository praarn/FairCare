import hashlib
import json
import secrets
import time
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"
RESET_TOKENS_FILE = DATA_DIR / "reset_tokens.json"

SESSION_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days
RESET_TOKEN_TTL_SECONDS = 60 * 60  # 1 hour
PBKDF2_ITERATIONS = 200_000


# ---------- tiny JSON-file "database" helpers ----------
# Deliberately simple (file-backed, not a real DB) to match the rest of
# this project's approach — swap for Postgres/Supabase in a later pass.
# encoding="utf-8" is required explicitly everywhere: see data_loader.py's
# comment — Windows defaults to cp1252 otherwise and silently breaks on
# any non-ASCII content.

def _read_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else default


def _write_json(path: Path, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_users() -> List[Dict]:
    return _read_json(USERS_FILE, [])


def _save_users(users: List[Dict]) -> None:
    _write_json(USERS_FILE, users)


def _load_sessions() -> Dict[str, Dict]:
    return _read_json(SESSIONS_FILE, {})


def _save_sessions(sessions: Dict[str, Dict]) -> None:
    _write_json(SESSIONS_FILE, sessions)


def _load_reset_tokens() -> Dict[str, Dict]:
    return _read_json(RESET_TOKENS_FILE, {})


def _save_reset_tokens(tokens: Dict[str, Dict]) -> None:
    _write_json(RESET_TOKENS_FILE, tokens)


# ---------- password hashing (stdlib only, no bcrypt dependency) ----------

def hash_password(password: str, salt_hex: Optional[str] = None) -> tuple[str, str]:
    salt_hex = salt_hex or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), PBKDF2_ITERATIONS
    )
    return digest.hex(), salt_hex


def _verify_password(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    digest, _ = hash_password(password, salt_hex)
    return secrets.compare_digest(digest, expected_hash_hex)


# ---------- public API used by the router ----------

def _public_user(user: Dict) -> Dict:
    return {"id": user["id"], "name": user["name"], "email": user["email"]}


def create_user(name: str, email: str, password: str) -> Dict:
    email = email.strip().lower()
    users = _load_users()
    if any(u["email"] == email for u in users):
        raise ValueError("An account with this email already exists.")

    password_hash, salt = hash_password(password)
    user = {
        "id": secrets.token_hex(8),
        "name": name.strip(),
        "email": email,
        "password_hash": password_hash,
        "password_salt": salt,
        "created_at": time.time(),
    }
    users.append(user)
    _save_users(users)
    return _public_user(user)


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    email = email.strip().lower()
    users = _load_users()
    for user in users:
        if user["email"] == email:
            if _verify_password(password, user["password_salt"], user["password_hash"]):
                return _public_user(user)
            return None
    return None


def create_session(email: str) -> str:
    token = secrets.token_urlsafe(32)
    sessions = _load_sessions()
    sessions[token] = {"email": email.strip().lower(), "expires_at": time.time() + SESSION_TTL_SECONDS}
    _save_sessions(sessions)
    return token


def get_user_by_session(token: str) -> Optional[Dict]:
    sessions = _load_sessions()
    session = sessions.get(token)
    if not session or session["expires_at"] < time.time():
        return None
    users = _load_users()
    for user in users:
        if user["email"] == session["email"]:
            return _public_user(user)
    return None


def delete_session(token: str) -> None:
    sessions = _load_sessions()
    sessions.pop(token, None)
    _save_sessions(sessions)


def create_reset_token(email: str) -> Optional[str]:
    """Returns None if no account exists for this email (caller decides
    whether to reveal that, to avoid leaking which emails are registered)."""
    email = email.strip().lower()
    users = _load_users()
    if not any(u["email"] == email for u in users):
        return None

    token = secrets.token_urlsafe(24)
    tokens = _load_reset_tokens()
    tokens[token] = {"email": email, "expires_at": time.time() + RESET_TOKEN_TTL_SECONDS}
    _save_reset_tokens(tokens)
    return token


def reset_password(token: str, new_password: str) -> bool:
    tokens = _load_reset_tokens()
    entry = tokens.get(token)
    if not entry or entry["expires_at"] < time.time():
        return False

    users = _load_users()
    for user in users:
        if user["email"] == entry["email"]:
            password_hash, salt = hash_password(new_password)
            user["password_hash"] = password_hash
            user["password_salt"] = salt
            _save_users(users)
            tokens.pop(token, None)
            _save_reset_tokens(tokens)
            return True
    return False
