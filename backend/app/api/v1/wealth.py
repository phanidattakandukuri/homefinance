from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user, household_member
from app.db.session import get_db
from app.models.auth import User
from app.models.wealth import Asset, Investment, InvestmentInstrument, InvestmentTransaction, InvestmentValuation, Liability, LiabilityPayment
from app.schemas.wealth import *
from app.services.finance import emi_schedule, xirr
router = APIRouter(prefix="/households/{household_id}/wealth", tags=["wealth"])
def auth(household_id, member_id, user, db): household_member(household_id, db, user); return member_id
@router.post("/instruments", response_model=InstrumentResponse, status_code=201)
def instrument(household_id: UUID, p: InstrumentCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); x=InvestmentInstrument(household_id=household_id, **p.model_dump()); db.add(x); db.flush(); return x
@router.post("/investments", response_model=InvestmentResponse, status_code=201)
def investment(household_id: UUID, p: InvestmentCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    auth(household_id,p.member_id,user,db); x=Investment(household_id=household_id, **p.model_dump()); db.add(x); db.flush(); return x
@router.get("/investments", response_model=list[InvestmentResponse])
def investments(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    actor = household_member(household_id, db, user); q = select(Investment).where(Investment.household_id==household_id)
    if actor.role not in {"owner", "admin"}: q = q.where(Investment.member_id == actor.id)
    return db.scalars(q).all()
@router.get("/instruments", response_model=list[InstrumentResponse])
def instruments(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); return [{"id":x.id,"name":x.name,"category":x.category,"identifier":x.identifier,"currency":x.currency} for x in db.scalars(select(InvestmentInstrument).where(InvestmentInstrument.household_id==household_id))]
@router.get("/investments/{investment_id}/transactions", response_model=list[InvestmentTransactionResponse])
def investment_transactions(household_id: UUID, investment_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    inv = db.get(Investment, investment_id)
    if not inv or inv.household_id != household_id: raise HTTPException(404, "Investment not found")
    return db.scalars(select(InvestmentTransaction).where(InvestmentTransaction.investment_id == investment_id).order_by(InvestmentTransaction.transaction_date.desc())).all()
@router.post("/investments/{investment_id}/transactions", response_model=InvestmentTransactionResponse, status_code=201)
def investment_transaction(household_id: UUID, investment_id: UUID, p: InvestmentTransactionCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id,db,user); inv=db.get(Investment,investment_id)
    if not inv or inv.household_id != household_id: raise HTTPException(404,"Investment not found")
    x=InvestmentTransaction(investment_id=investment_id,**p.model_dump()); db.add(x); db.flush(); return x
@router.get("/investments/{investment_id}/valuations", response_model=list[ValuationResponse])
def valuations(household_id: UUID, investment_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    inv = db.get(Investment, investment_id)
    if not inv or inv.household_id != household_id: raise HTTPException(404, "Investment not found")
    return db.scalars(select(InvestmentValuation).where(InvestmentValuation.investment_id == investment_id).order_by(InvestmentValuation.valuation_date.desc())).all()
@router.post("/investments/{investment_id}/valuations", response_model=ValuationResponse, status_code=201)
def valuation(household_id: UUID, investment_id: UUID, p: ValuationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id,db,user); inv=db.get(Investment,investment_id)
    if not inv or inv.household_id != household_id: raise HTTPException(404,"Investment not found")
    x=InvestmentValuation(investment_id=investment_id,**p.model_dump()); db.add(x); db.flush(); return x

@router.get("/investments/{investment_id}/performance")
def investment_performance(household_id: UUID, investment_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    investment = db.get(Investment, investment_id)
    if not investment or investment.household_id != household_id: raise HTTPException(404, "Investment not found")
    flows = []
    invested = Decimal("0")
    for item in db.scalars(select(InvestmentTransaction).where(InvestmentTransaction.investment_id == investment_id).order_by(InvestmentTransaction.transaction_date)):
        amount = abs(item.cash_flow)
        if item.transaction_type.lower() in {"buy", "contribution", "purchase", "deposit"}:
            amount = -amount; invested += abs(item.cash_flow)
        flows.append((item.transaction_date, amount))
    latest = db.scalar(select(InvestmentValuation).where(InvestmentValuation.investment_id == investment_id).order_by(InvestmentValuation.valuation_date.desc()).limit(1))
    current_value = latest.current_value if latest else Decimal("0")
    if latest: flows.append((latest.valuation_date, current_value))
    return {"investment_id": investment_id, "invested_amount": invested, "current_value": current_value, "gain_loss": current_value - invested, "xirr": xirr(flows)}
@router.post("/assets", response_model=AssetResponse, status_code=201)
def asset(household_id: UUID,p: AssetCreate,user: User=Depends(current_user),db: Session=Depends(get_db)):
    auth(household_id,p.member_id,user,db); x=Asset(household_id=household_id,**p.model_dump()); db.add(x); db.flush(); return x
@router.get("/assets", response_model=list[AssetResponse])
def assets(household_id: UUID, user: User=Depends(current_user), db: Session=Depends(get_db)):
    actor = household_member(household_id,db,user); q = select(Asset).where(Asset.household_id==household_id)
    if actor.role not in {"owner", "admin"}: q = q.where(Asset.member_id == actor.id)
    return db.scalars(q).all()
@router.post("/liabilities", response_model=LiabilityResponse, status_code=201)
def liability(household_id: UUID,p: LiabilityCreate,user: User=Depends(current_user),db: Session=Depends(get_db)):
    auth(household_id,p.member_id,user,db); x=Liability(household_id=household_id,**p.model_dump()); db.add(x); db.flush(); return x
@router.get("/liabilities", response_model=list[LiabilityResponse])
def liabilities(household_id: UUID, user: User=Depends(current_user), db: Session=Depends(get_db)):
    actor = household_member(household_id,db,user); q = select(Liability).where(Liability.household_id==household_id)
    if actor.role not in {"owner", "admin"}: q = q.where(Liability.member_id == actor.id)
    return db.scalars(q).all()

@router.get("/liabilities/{liability_id}/payments", response_model=list[LiabilityPaymentResponse])
def liability_payments(household_id: UUID, liability_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    liability = db.get(Liability, liability_id)
    if not liability or liability.household_id != household_id: raise HTTPException(404, "Liability not found")
    return db.scalars(select(LiabilityPayment).where(LiabilityPayment.liability_id == liability_id).order_by(LiabilityPayment.payment_date.desc())).all()

@router.post("/liabilities/{liability_id}/payments", response_model=LiabilityPaymentResponse, status_code=201)
def liability_payment(household_id: UUID, liability_id: UUID, p: LiabilityPaymentCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    liability = db.get(Liability, liability_id)
    if not liability or liability.household_id != household_id: raise HTTPException(404, "Liability not found")
    if p.principal is not None and p.interest is not None and p.principal + p.interest > p.amount:
        raise HTTPException(422, "Principal plus interest cannot exceed payment amount")
    payment = LiabilityPayment(liability_id=liability_id, **p.model_dump())
    db.add(payment)
    if p.principal is not None and liability.current_outstanding is not None:
        liability.current_outstanding = max(Decimal("0"), liability.current_outstanding - p.principal)
    db.flush()
    return payment

@router.get("/liabilities/{liability_id}/schedule")
def loan_schedule(household_id: UUID, liability_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    liability = db.get(Liability, liability_id)
    if not liability or liability.household_id != household_id: raise HTTPException(404, "Liability not found")
    if not liability.current_outstanding or not liability.emi or liability.interest_rate is None or not liability.remaining_tenure_months:
        raise HTTPException(422, "Loan principal, EMI, interest rate, and remaining tenure are required")
    schedule = emi_schedule(liability.current_outstanding, liability.interest_rate, liability.emi, liability.remaining_tenure_months)
    return {"liability_id": liability_id, "interest_type": liability.interest_type, "schedule": schedule, "total_interest": sum((row["interest"] for row in schedule), Decimal("0"))}
