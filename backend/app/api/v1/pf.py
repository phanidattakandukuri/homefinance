from datetime import date
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user, household_member
from app.db.session import get_db
from app.models.auth import User
from app.models.pf import GratuityProfile, ProvidentFundAccount, ProvidentFundEntry
from app.schemas.pf import *

router = APIRouter(prefix="/households/{household_id}/pf", tags=["provident-fund"])

def authorize(household_id, member_id, user, db):
    household_member(household_id, db, user)
    return member_id

@router.post("/accounts", response_model=PFAccountResponse, status_code=201)
def create_account(household_id: UUID, payload: PFAccountCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    authorize(household_id, payload.member_id, user, db)
    if payload.scheme.upper() not in {"EPF", "EPS", "COMBINED"}: raise HTTPException(422, "scheme must be EPF, EPS, or COMBINED")
    account = ProvidentFundAccount(household_id=household_id, **payload.model_dump())
    db.add(account); db.flush(); return account

@router.get("/accounts", response_model=list[PFAccountResponse])
def list_accounts(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    actor = household_member(household_id, db, user); q = select(ProvidentFundAccount).where(ProvidentFundAccount.household_id == household_id)
    if actor.role not in {"owner", "admin"}: q = q.where(ProvidentFundAccount.member_id == actor.id)
    return db.scalars(q).all()

@router.post("/accounts/{account_id}/entries", response_model=PFEntryResponse, status_code=201)
def create_entry(household_id: UUID, account_id: UUID, payload: PFEntryCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    account = db.get(ProvidentFundAccount, account_id)
    if not account or account.household_id != household_id: raise HTTPException(404, "PF account not found")
    entry = ProvidentFundEntry(account_id=account_id, **payload.model_dump())
    db.add(entry); db.flush(); return entry

@router.get("/accounts/{account_id}/entries", response_model=list[PFEntryResponse])
def list_entries(household_id: UUID, account_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    account = db.get(ProvidentFundAccount, account_id)
    if not account or account.household_id != household_id: raise HTTPException(404, "PF account not found")
    return db.scalars(select(ProvidentFundEntry).where(ProvidentFundEntry.account_id == account_id).order_by(ProvidentFundEntry.entry_date.desc())).all()

@router.post("/gratuity", response_model=GratuityResponse, status_code=201)
def create_gratuity(household_id: UUID, payload: GratuityCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    authorize(household_id, payload.member_id, user, db)
    years = Decimal(max(0, (date.today() - payload.joining_date).days)) / Decimal("365.25")
    estimated = ((payload.basic_salary + payload.da_salary) * Decimal("15") / Decimal("26") * years).quantize(Decimal("0.01"))
    item = GratuityProfile(household_id=household_id, estimated_amount=estimated, **payload.model_dump())
    db.add(item); db.flush(); return item

@router.get("/gratuity", response_model=list[GratuityResponse])
def list_gratuity(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    return db.scalars(select(GratuityProfile).where(GratuityProfile.household_id == household_id)).all()
