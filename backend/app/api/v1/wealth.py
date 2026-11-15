from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user, household_member
from app.db.session import get_db
from app.models.auth import User
from app.models.wealth import Asset, Investment, InvestmentInstrument, InvestmentTransaction, InvestmentValuation, Liability, LiabilityPayment
from app.schemas.wealth import *
router = APIRouter(prefix="/households/{household_id}/wealth", tags=["wealth"])
def auth(household_id, member_id, user, db): household_member(household_id, db, user); return member_id
@router.post("/instruments", response_model=InstrumentResponse, status_code=201)
def instrument(household_id: UUID, p: InstrumentCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); x=InvestmentInstrument(household_id=household_id, **p.model_dump()); db.add(x); db.flush(); return x
@router.post("/investments", response_model=InvestmentResponse, status_code=201)
def investment(household_id: UUID, p: InvestmentCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    auth(household_id,p.member_id,user,db); x=Investment(household_id=household_id, **p.model_dump()); db.add(x); db.flush(); return x
@router.get("/investments")
def investments(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); return [{"id":x.id,"member_id":x.member_id,"instrument_id":x.instrument_id} for x in db.scalars(select(Investment).where(Investment.household_id==household_id))]
@router.get("/instruments")
def instruments(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); return [{"id":x.id,"name":x.name,"category":x.category,"identifier":x.identifier,"currency":x.currency} for x in db.scalars(select(InvestmentInstrument).where(InvestmentInstrument.household_id==household_id))]
@router.post("/investments/{investment_id}/transactions", status_code=201)
def investment_transaction(household_id: UUID, investment_id: UUID, p: InvestmentTransactionCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id,db,user); inv=db.get(Investment,investment_id)
    if not inv or inv.household_id != household_id: raise HTTPException(404,"Investment not found")
    x=InvestmentTransaction(investment_id=investment_id,**p.model_dump()); db.add(x); db.flush(); return {"id":x.id}
@router.post("/investments/{investment_id}/valuations", status_code=201)
def valuation(household_id: UUID, investment_id: UUID, p: ValuationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id,db,user); inv=db.get(Investment,investment_id)
    if not inv or inv.household_id != household_id: raise HTTPException(404,"Investment not found")
    x=InvestmentValuation(investment_id=investment_id,**p.model_dump()); db.add(x); db.flush(); return {"id":x.id}
@router.post("/assets", response_model=WealthResponse, status_code=201)
def asset(household_id: UUID,p: AssetCreate,user: User=Depends(current_user),db: Session=Depends(get_db)):
    auth(household_id,p.member_id,user,db); x=Asset(household_id=household_id,**p.model_dump()); db.add(x); db.flush(); return x
@router.get("/assets")
def assets(household_id: UUID, user: User=Depends(current_user), db: Session=Depends(get_db)):
    household_member(household_id,db,user); return [{"id":x.id,"name":x.name,"category":x.category,"current_value":x.current_value,"valuation_date":x.valuation_date} for x in db.scalars(select(Asset).where(Asset.household_id==household_id))]
@router.post("/liabilities", response_model=WealthResponse, status_code=201)
def liability(household_id: UUID,p: LiabilityCreate,user: User=Depends(current_user),db: Session=Depends(get_db)):
    auth(household_id,p.member_id,user,db); x=Liability(household_id=household_id,**p.model_dump()); db.add(x); db.flush(); return x
@router.get("/liabilities")
def liabilities(household_id: UUID, user: User=Depends(current_user), db: Session=Depends(get_db)):
    household_member(household_id,db,user); return [{"id":x.id,"name":x.name,"category":x.category,"current_outstanding":x.current_outstanding} for x in db.scalars(select(Liability).where(Liability.household_id==household_id))]
