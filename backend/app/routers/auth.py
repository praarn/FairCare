
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.logging_config import get_logger
from app.rate_limit import limiter
from app.schemas import (
    AuthResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    ResetPasswordRequest,
    SignupRequest,
    UserOut,
)
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])
log = get_logger("faircare.auth")


def _extract_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return authorization.split(" ", 1)[1]


@router.post("/signup", response_model=AuthResponse)
@limiter.limit(settings.rate_limit_auth)
def signup(request: Request, payload: SignupRequest, db: Session = Depends(get_db)):
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    if "@" not in payload.email or "." not in payload.email:
        raise HTTPException(status_code=400, detail="Enter a valid email address.")
    try:
        user = auth_service.create_user(db, payload.name, payload.email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    token = auth_service.create_session(db, user["email"])
    return AuthResponse(token=token, user=UserOut(**user))


@router.post("/login", response_model=AuthResponse)
@limiter.limit(settings.rate_limit_auth)
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = auth_service.create_session(db, user["email"])
    return AuthResponse(token=token, user=UserOut(**user))


@router.post("/logout")
def logout(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if authorization and authorization.lower().startswith("bearer "):
        auth_service.delete_session(db, authorization.split(" ", 1)[1])
    return {"status": "ok"}


@router.get("/me", response_model=UserOut)
def me(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    token = _extract_token(authorization)
    user = auth_service.get_user_by_session(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    return UserOut(**user)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
@limiter.limit(settings.rate_limit_auth)
def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    token = auth_service.create_reset_token(db, payload.email)

    # Same message whether or not the account exists, so this endpoint can't be
    # used to enumerate registered emails. In development the token is returned
    # in the body for convenience (no mail service is wired up); in production
    # it is only logged (stand-in for the email send) and never returned.
    if settings.is_production:
        if token:
            log.info("password_reset_issued", email=payload.email.strip().lower())
        return ForgotPasswordResponse(
            message="If an account exists for that email, a reset link has been sent.",
            reset_token=None,
            note="A reset link is emailed when the account exists.",
        )

    return ForgotPasswordResponse(
        message="If an account exists for that email, a reset link has been generated.",
        reset_token=token,
        note="Development mode: no email service is configured, so the reset link is shown here directly.",
    )


@router.post("/reset-password")
@limiter.limit(settings.rate_limit_auth)
def reset_password_endpoint(
    request: Request,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    success = auth_service.reset_password(db, payload.token, payload.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="This reset link is invalid or has expired.")
    return {"status": "ok"}
