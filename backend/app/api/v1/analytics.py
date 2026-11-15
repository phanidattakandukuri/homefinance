from datetime import date, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user, household_member
from app.db.session import get_db
from app.models.analytics import FinancialSnapshot, SnapshotAudit
from app.models.auth import User
from app.schemas.analytics import DashboardResponse, SnapshotResponse
from app.services.analytics import dashboard
router=APIRouter(prefix="/households/{household_id}/analytics",tags=["analytics"])
def period(period_type, start, end):
    today=date.today()
    if period_type == "current_month": return today.replace(day=1), today
    if period_type == "previous_month":
        first=today.replace(day=1); prev=first-timedelta(days=1); return prev.replace(day=1), prev
    if period_type == "calendar_year": return today.replace(month=1,day=1), today
    if period_type == "financial_year": return date(today.year if today.month >= 4 else today.year-1,4,1), today
    if not start or not end: raise HTTPException(422,"start and end are required")
    return start,end
@router.get("/household",response_model=DashboardResponse)
def household_dashboard(household_id:UUID, period_type:str="current_month", start:date|None=None,end:date|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
    household_member(household_id,db,user); s,e=period(period_type,start,end); return dashboard(db,household_id,s,e)
@router.get("/members/{member_id}",response_model=DashboardResponse)
def member_dashboard(household_id:UUID,member_id:UUID,period_type:str="current_month",start:date|None=None,end:date|None=None,user:User=Depends(current_user),db:Session=Depends(get_db)):
    household_member(household_id,db,user); s,e=period(period_type,start,end); return dashboard(db,household_id,s,e,member_id)
@router.post("/snapshots",response_model=SnapshotResponse)
def create_snapshot(household_id:UUID,start:date,end:date,reason:str="scheduled",user:User=Depends(current_user),db:Session=Depends(get_db)):
    household_member(household_id,db,user); existing=db.scalar(select(FinancialSnapshot).where(FinancialSnapshot.household_id==household_id,FinancialSnapshot.period_start==start,FinancialSnapshot.period_end==end))
    if existing: raise HTTPException(409,"Snapshot already exists; use controlled recalculation")
    x=FinancialSnapshot(household_id=household_id,period_start=start,period_end=end,payload=dashboard(db,household_id,start,end),recalculation_reason=reason); db.add(x); db.flush(); return {"id":x.id,"period_start":start,"period_end":end,"payload":x.payload,"calculated_at":str(x.calculated_at)}
@router.get("/snapshots")
def snapshots(household_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    household_member(household_id,db,user); return db.scalars(select(FinancialSnapshot).where(FinancialSnapshot.household_id==household_id).order_by(FinancialSnapshot.period_start.desc())).all()
