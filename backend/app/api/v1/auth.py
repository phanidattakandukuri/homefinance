from datetime import datetime, timezone
import hashlib
import secrets
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user
from app.core.security import create_token, hash_password, verify_password, decode_token, decode_token_version
from app.core.config import get_settings
from app.db.session import get_db
from app.models.auth import PasswordResetToken, User
from app.models.household import HouseholdInvitation, HouseholdMember
from app.schemas.auth import InvitationAcceptRequest, LoginRequest, PasswordChangeRequest, PasswordResetConfirm, PasswordResetRequest, PasswordResetResponse, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(409, "Email is already registered")
    user = User(email=payload.email.lower(), full_name=payload.full_name, password_hash=hash_password(payload.password))
    db.add(user); db.flush(); return user

@router.post("/invitations/accept", response_model=UserResponse, status_code=201)
def accept_invitation(payload: InvitationAcceptRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(payload.invitation_token.encode()).hexdigest()
    invitation = db.scalar(select(HouseholdInvitation).where(HouseholdInvitation.token_hash == token_hash))
    if not invitation or invitation.accepted_at or invitation.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(400, "Invitation is invalid or expired")
    user = db.scalar(select(User).where(User.email == invitation.email))
    if not user:
        user = User(email=invitation.email, full_name=payload.full_name, password_hash=hash_password(payload.password))
        db.add(user); db.flush()
    elif not user.is_active:
        raise HTTPException(400, "User account is inactive")
    member = db.get(HouseholdMember, invitation.member_id)
    if not member: raise HTTPException(404, "Invited member no longer exists")
    member.user_id = user.id; member.membership_status = "active"
    invitation.accepted_at = datetime.now(timezone.utc)
    db.flush()
    return user

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return TokenResponse(access_token=create_token(user.id, "access", 15, user.token_version), refresh_token=create_token(user.id, "refresh", 60 * 24 * 30, user.token_version))

@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    try: user_id = decode_token(refresh_token, "refresh")
    except Exception: raise HTTPException(401, "Invalid refresh token")
    user = db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))
    if not user: raise HTTPException(401, "Invalid refresh token")
    if decode_token_version(refresh_token) != user.token_version: raise HTTPException(401, "Refresh token has been revoked")
    return TokenResponse(access_token=create_token(user.id, "access", 15, user.token_version), refresh_token=create_token(user.id, "refresh", 60 * 24 * 30, user.token_version))

@router.post("/logout", status_code=204)
def logout(user: User = Depends(current_user), db: Session = Depends(get_db)):
    user.token_version += 1
    db.flush()

@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)): return user

@router.post("/password", status_code=204)
def change_password(payload: PasswordChangeRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    user.password_hash = hash_password(payload.new_password)
    user.token_version += 1
    db.flush()

@router.post("/password/reset-request", response_model=PasswordResetResponse)
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    # Always return the same message to avoid account enumeration.
    user = db.scalar(select(User).where(User.email == payload.email.lower(), User.is_active.is_(True)))
    raw_token = None
    if user:
        raw_token = secrets.token_urlsafe(32)
        db.add(PasswordResetToken(user_id=user.id, token_hash=hashlib.sha256(raw_token.encode()).hexdigest(), expires_at=datetime.now(timezone.utc) + timedelta(minutes=30)))
        db.flush()
    response = {"message": "If an active account exists, password reset instructions have been prepared."}
    if raw_token and get_settings().app_env != "production": response["reset_token"] = raw_token
    return response

@router.post("/password/reset", status_code=204)
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    item = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == hashlib.sha256(payload.reset_token.encode()).hexdigest(), PasswordResetToken.used_at.is_(None)))
    if not item or item.expires_at <= datetime.now(timezone.utc): raise HTTPException(400, "Reset token is invalid or expired")
    user = db.get(User, item.user_id)
    if not user or not user.is_active: raise HTTPException(400, "Reset token is invalid or expired")
    user.password_hash = hash_password(payload.new_password); user.token_version += 1; item.used_at = datetime.now(timezone.utc); db.flush()
