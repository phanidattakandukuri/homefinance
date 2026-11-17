from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.v1.dependencies import current_user, household_member, require_admin
from app.db.session import get_db
from app.models.auth import User
from app.models.household import Household, HouseholdInvitation, HouseholdJoinCode, HouseholdMember
from app.schemas.household import HouseholdCreate, HouseholdResponse, HouseholdUpdate, InvitationCreate, InvitationResponse, JoinCodeResponse, JoinHouseholdRequest, MemberCreate, MemberResponse, MemberUpdate

router = APIRouter(prefix="/households", tags=["households"])

@router.post("", response_model=HouseholdResponse, status_code=201)
def create_household(payload: HouseholdCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household = Household(name=payload.name, base_currency=payload.base_currency.upper(), timezone=payload.timezone)
    db.add(household); db.flush()
    db.add(HouseholdMember(household_id=household.id, user_id=user.id, display_name=user.full_name, role="owner"))
    for name in payload.earning_member_names: db.add(HouseholdMember(household_id=household.id, display_name=name, role="member", user_id=None))
    db.flush(); return db.scalar(select(Household).options(selectinload(Household.members)).where(Household.id == household.id))

def get_household(household_id: UUID, db: Session) -> Household:
    household = db.scalar(select(Household).options(selectinload(Household.members)).where(Household.id == household_id))
    if not household: raise HTTPException(404, "Household not found")
    return household

@router.get("/{household_id}", response_model=HouseholdResponse)
def read_household(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); return get_household(household_id, db)

@router.post("/{household_id}/join-code", response_model=JoinCodeResponse)
def create_join_code(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_admin(household_id, db, user)
    raw = secrets.token_urlsafe(9).replace("-", "A").replace("_", "B").upper()[:10]
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    db.add(HouseholdJoinCode(household_id=household_id, created_by_user_id=user.id, code_hash=hashlib.sha256(raw.encode()).hexdigest(), expires_at=expires)); db.flush()
    return {"household_id": household_id, "code": raw, "expires_at": expires.isoformat()}

@router.post("/join", response_model=MemberResponse)
def join_household(payload: JoinHouseholdRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    hashed = hashlib.sha256(payload.code.strip().upper().encode()).hexdigest()
    join = db.scalar(select(HouseholdJoinCode).where(HouseholdJoinCode.code_hash == hashed, HouseholdJoinCode.revoked_at.is_(None), HouseholdJoinCode.expires_at > datetime.now(timezone.utc)))
    if not join: raise HTTPException(404, "Invalid or expired household code")
    existing = db.scalar(select(HouseholdMember).where(HouseholdMember.household_id == join.household_id, HouseholdMember.user_id == user.id))
    if existing:
        existing.membership_status = "active"; return existing
    member = HouseholdMember(household_id=join.household_id, user_id=user.id, display_name=user.full_name, email=user.email, role="member", membership_status="active")
    db.add(member); db.flush(); return member

@router.patch("/{household_id}", response_model=HouseholdResponse)
def update_household(household_id: UUID, payload: HouseholdUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_admin(household_id, db, user); household = get_household(household_id, db)
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(household, key, value.upper() if key == "base_currency" else value)
    db.flush(); return household

@router.get("/{household_id}/members", response_model=list[MemberResponse])
def members(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); return get_household(household_id, db).members

@router.get("/{household_id}/members/{member_id}", response_model=MemberResponse)
def read_member(household_id: UUID, member_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    member = db.get(HouseholdMember, member_id)
    if not member or member.household_id != household_id:
        raise HTTPException(404, "Member not found")
    return member

@router.post("/{household_id}/members", response_model=MemberResponse, status_code=201)
def add_member(household_id: UUID, payload: MemberCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_admin(household_id, db, user)
    if payload.role not in {"admin", "member", "viewer"}: raise HTTPException(400, "Invalid member role")
    if payload.role == "admin" and not user.memberships: raise HTTPException(403, "Insufficient privileges")
    member = HouseholdMember(household_id=household_id, **payload.model_dump())
    db.add(member); db.flush(); return member

@router.post("/{household_id}/invitations", response_model=InvitationResponse, status_code=201)
def invite_member(household_id: UUID, payload: InvitationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_admin(household_id, db, user)
    if payload.role not in {"admin", "member", "viewer"}: raise HTTPException(400, "Invalid member role")
    email = payload.email.lower()
    member = HouseholdMember(household_id=household_id, display_name=payload.display_name, email=email, role=payload.role, membership_status="pending", relationship_to_household=payload.relationship_to_household)
    db.add(member); db.flush()
    raw_token = secrets.token_urlsafe(32)
    invitation = HouseholdInvitation(household_id=household_id, member_id=member.id, invited_by_user_id=user.id, email=email, token_hash=hashlib.sha256(raw_token.encode()).hexdigest(), expires_at=datetime.now(timezone.utc) + timedelta(days=7))
    db.add(invitation); db.flush()
    return {"invitation_id": invitation.id, "member_id": member.id, "email": email, "expires_at": invitation.expires_at.isoformat(), "invitation_token": raw_token}

@router.patch("/{household_id}/members/{member_id}", response_model=MemberResponse)
def update_member(household_id: UUID, member_id: UUID, payload: MemberUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    actor = require_admin(household_id, db, user); member = db.get(HouseholdMember, member_id)
    if not member or member.household_id != household_id: raise HTTPException(404, "Member not found")
    values = payload.model_dump(exclude_unset=True)
    requested_role = values.get("role")
    if member.role == "owner" or requested_role == "owner" or (actor.role != "owner" and requested_role == "admin"):
        raise HTTPException(403, "Owner-only role change")
    if requested_role and requested_role not in {"admin", "member", "viewer"}:
        raise HTTPException(400, "Invalid member role")
    if values.get("membership_status") not in {None, "active", "inactive", "pending"}:
        raise HTTPException(400, "Invalid membership status")
    for key, value in values.items(): setattr(member, key, value)
    db.flush(); return member

@router.delete("/{household_id}/members/{member_id}", status_code=204)
def remove_member(household_id: UUID, member_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    actor = require_admin(household_id, db, user); member = db.get(HouseholdMember, member_id)
    if not member or member.household_id != household_id: raise HTTPException(404, "Member not found")
    if member.role == "owner" or (member.role == "admin" and actor.role != "owner"): raise HTTPException(403, "Cannot remove this member")
    # Preserve historical financial records; removal is a deactivation.
    member.membership_status = "inactive"
    db.flush()
