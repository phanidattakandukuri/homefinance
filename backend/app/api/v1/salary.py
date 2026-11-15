from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user, household_member
from app.db.session import get_db
from app.models.auth import User
from app.models.salary import SalaryAudit, SalaryRecord
from app.schemas.salary import SalaryBreakdown, SalaryCreate, SalaryResponse, SalaryUpdate
from app.services.salary import breakdown

router = APIRouter(prefix="/households/{household_id}/members/{member_id}/salary", tags=["salary"])

def member_check(household_id, member_id, user, db):
    actor = household_member(household_id, db, user)
    member = db.get(__import__('app.models.household', fromlist=['HouseholdMember']).HouseholdMember, member_id)
    if not member or member.household_id != household_id: raise HTTPException(404, "Member not found")
    return actor, member

def ensure_period(record, db, exclude=None):
    overlap = db.scalar(select(SalaryRecord).where(SalaryRecord.member_id == record.member_id, SalaryRecord.id != exclude,
        SalaryRecord.effective_from <= (record.effective_to or date.max),
        or_(SalaryRecord.effective_to.is_(None), SalaryRecord.effective_to >= record.effective_from)))
    if overlap: raise HTTPException(409, "Salary effective period overlaps an existing record")

@router.post("", response_model=SalaryResponse, status_code=201)
def add_salary(household_id: UUID, member_id: UUID, payload: SalaryCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    member_check(household_id, member_id, user, db)
    record = SalaryRecord(household_id=household_id, member_id=member_id, **payload.model_dump())
    ensure_period(record, db); db.add(record); db.flush(); db.add(SalaryAudit(salary_id=record.id, changed_by_user_id=user.id, action="created")); return record

@router.get("", response_model=list[SalaryResponse])
def list_salary(household_id: UUID, member_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    member_check(household_id, member_id, user, db)
    return db.scalars(select(SalaryRecord).where(SalaryRecord.household_id == household_id, SalaryRecord.member_id == member_id).order_by(SalaryRecord.effective_from.desc())).all()

@router.get("/current", response_model=SalaryResponse | None)
def current_salary(household_id: UUID, member_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    member_check(household_id, member_id, user, db)
    return db.scalar(select(SalaryRecord).where(SalaryRecord.household_id == household_id, SalaryRecord.member_id == member_id, SalaryRecord.effective_from <= date.today(), or_(SalaryRecord.effective_to.is_(None), SalaryRecord.effective_to >= date.today())).order_by(SalaryRecord.effective_from.desc()))

@router.patch("/{salary_id}", response_model=SalaryResponse)
def update_salary(household_id: UUID, member_id: UUID, salary_id: UUID, payload: SalaryUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    member_check(household_id, member_id, user, db); record = db.get(SalaryRecord, salary_id)
    if not record or record.household_id != household_id or record.member_id != member_id: raise HTTPException(404, "Salary record not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(record, key, value)
    ensure_period(record, db, salary_id); db.flush(); db.add(SalaryAudit(salary_id=record.id, changed_by_user_id=user.id, action="updated")); return record

@router.post("/revision", response_model=SalaryResponse, status_code=201)
def revision(household_id: UUID, member_id: UUID, payload: SalaryCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return add_salary(household_id, member_id, payload, user, db)

@router.get("/{salary_id}/breakdown", response_model=SalaryBreakdown)
def salary_breakdown(household_id: UUID, member_id: UUID, salary_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    member_check(household_id, member_id, user, db); record = db.get(SalaryRecord, salary_id)
    if not record or record.household_id != household_id or record.member_id != member_id: raise HTTPException(404, "Salary record not found")
    return breakdown(record)
