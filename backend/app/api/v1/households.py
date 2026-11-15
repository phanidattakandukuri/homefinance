from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.v1.dependencies import current_user, household_member, require_admin
from app.db.session import get_db
from app.models.auth import User
from app.models.household import Household, HouseholdMember
from app.schemas.household import HouseholdCreate, HouseholdResponse, HouseholdUpdate, MemberCreate, MemberResponse, MemberRoleUpdate

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

@router.patch("/{household_id}", response_model=HouseholdResponse)
def update_household(household_id: UUID, payload: HouseholdUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_admin(household_id, db, user); household = get_household(household_id, db)
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(household, key, value.upper() if key == "base_currency" else value)
    db.flush(); return household

@router.get("/{household_id}/members", response_model=list[MemberResponse])
def members(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); return get_household(household_id, db).members

@router.post("/{household_id}/members", response_model=MemberResponse, status_code=201)
def add_member(household_id: UUID, payload: MemberCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_admin(household_id, db, user)
    if payload.role not in {"admin", "member", "viewer"}: raise HTTPException(400, "Invalid member role")
    if payload.role == "admin" and not user.memberships: raise HTTPException(403, "Insufficient privileges")
    member = HouseholdMember(household_id=household_id, user_id=payload.user_id, display_name=payload.display_name, role=payload.role)
    db.add(member); db.flush(); return member

@router.patch("/{household_id}/members/{member_id}", response_model=MemberResponse)
def update_member(household_id: UUID, member_id: UUID, payload: MemberRoleUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    actor = require_admin(household_id, db, user); member = db.get(HouseholdMember, member_id)
    if not member or member.household_id != household_id: raise HTTPException(404, "Member not found")
    if member.role == "owner" or payload.role == "owner" or (actor.role != "owner" and payload.role == "admin"): raise HTTPException(403, "Owner-only role change")
    member.role = payload.role; db.flush(); return member

@router.delete("/{household_id}/members/{member_id}", status_code=204)
def remove_member(household_id: UUID, member_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    actor = require_admin(household_id, db, user); member = db.get(HouseholdMember, member_id)
    if not member or member.household_id != household_id: raise HTTPException(404, "Member not found")
    if member.role == "owner" or (member.role == "admin" and actor.role != "owner"): raise HTTPException(403, "Cannot remove this member")
    db.delete(member)
