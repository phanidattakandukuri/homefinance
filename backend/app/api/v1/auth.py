from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user
from app.core.security import create_token, hash_password, verify_password, decode_token
from app.db.session import get_db
from app.models.auth import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(409, "Email is already registered")
    user = User(email=payload.email.lower(), full_name=payload.full_name, password_hash=hash_password(payload.password))
    db.add(user); db.flush(); return user

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return TokenResponse(access_token=create_token(user.id, "access", 15), refresh_token=create_token(user.id, "refresh", 60 * 24 * 30))

@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    try: user_id = decode_token(refresh_token, "refresh")
    except Exception: raise HTTPException(401, "Invalid refresh token")
    user = db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))
    if not user: raise HTTPException(401, "Invalid refresh token")
    return TokenResponse(access_token=create_token(user.id, "access", 15), refresh_token=create_token(user.id, "refresh", 60 * 24 * 30))

@router.post("/logout", status_code=204)
def logout(_: User = Depends(current_user)):
    return None

@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)): return user
