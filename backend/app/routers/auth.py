from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.schemas import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    UserOut,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _extract_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return authorization.split(" ", 1)[1]


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest):
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    if "@" not in payload.email or "." not in payload.email:
        raise HTTPException(status_code=400, detail="Enter a valid email address.")
    try:
        user = auth_service.create_user(payload.name, payload.email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    token = auth_service.create_session(user["email"])
    return AuthResponse(token=token, user=UserOut(**user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    user = auth_service.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = auth_service.create_session(user["email"])
    return AuthResponse(token=token, user=UserOut(**user))


@router.post("/logout")
def logout(authorization: Optional[str] = Header(default=None)):
    if authorization and authorization.lower().startswith("bearer "):
        auth_service.delete_session(authorization.split(" ", 1)[1])
    return {"status": "ok"}


@router.get("/me", response_model=UserOut)
def me(authorization: Optional[str] = Header(default=None)):
    token = _extract_token(authorization)
    user = auth_service.get_user_by_session(token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    return UserOut(**user)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest):
    token = auth_service.create_reset_token(payload.email)
    # Deliberately the same message whether or not the account exists, so
    # this endpoint can't be used to check which emails are registered.
    # No email service is configured in this project, so — rather than
    # silently pretending to send one — the token is returned directly
    # for the frontend to show on screen with a clear "would be emailed
    # in production" note.
    return ForgotPasswordResponse(
        message="If an account exists for that email, a reset link has been generated.",
        reset_token=token,
        note="No email service is configured yet, so this reset link is shown here directly instead of being emailed.",
    )


@router.post("/reset-password")
def reset_password_endpoint(payload: ResetPasswordRequest):
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    success = auth_service.reset_password(payload.token, payload.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="This reset link is invalid or has expired.")
    return {"status": "ok"}
