from uuid import UUID
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import decode_token, decode_token_version
from app.db.session import get_db
from app.models.auth import User
from app.models.household import HouseholdMember

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try: user_id = decode_token(token, "access")
    except (jwt.InvalidTokenError, ValueError, KeyError): raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))
    if not user: raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    try:
        if decode_token_version(token) != user.token_version: raise HTTPException(status_code=401, detail="Token has been revoked")
    except HTTPException: raise
    except (jwt.InvalidTokenError, ValueError, KeyError): raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

def household_member(household_id: UUID, db: Session, user: User) -> HouseholdMember:
    member = db.scalar(select(HouseholdMember).where(HouseholdMember.household_id == household_id, HouseholdMember.user_id == user.id, HouseholdMember.membership_status == "active"))
    if not member: raise HTTPException(status_code=403, detail="Household membership required")
    return member

def require_admin(household_id: UUID, db: Session, user: User) -> HouseholdMember:
    member = household_member(household_id, db, user)
    if member.role not in {"owner", "admin"}: raise HTTPException(status_code=403, detail="Owner or admin role required")
    return member

def authorize_member_view(household_id: UUID, member_id: UUID, db: Session, user: User) -> HouseholdMember:
    actor = household_member(household_id, db, user)
    target = db.get(HouseholdMember, member_id)
    if not target or target.household_id != household_id or target.membership_status != "active":
        raise HTTPException(status_code=404, detail="Member not found")
    if target.user_id != user.id and actor.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Permission to view this member is required")
    return target
