from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user,household_member
from app.db.session import get_db
from app.models.auth import User
from app.models.planning import Budget,Goal,RecurringTransaction
from app.models.transaction import Transaction
from app.schemas.planning import BudgetCreate,BudgetResponse,GoalCreate,GoalResponse,RecurringCreate
router=APIRouter(prefix="/households/{household_id}",tags=["planning"])
def auth(h,u,d): household_member(h,d,u)
@router.post("/budgets",response_model=BudgetResponse,status_code=201)
def budget(household_id,p:BudgetCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    auth(household_id,user,db); x=Budget(household_id=household_id,**p.model_dump()); db.add(x); db.flush(); return x
@router.get("/budgets",response_model=list[BudgetResponse])
def budgets(household_id,user:User=Depends(current_user),db:Session=Depends(get_db)): auth(household_id,user,db); return db.scalars(select(Budget).where(Budget.household_id==household_id)).all()
@router.get("/budgets/{budget_id}/progress")
def budget_progress(household_id,budget_id,user:User=Depends(current_user),db:Session=Depends(get_db)):
    auth(household_id,user,db); b=db.get(Budget,budget_id)
    if not b or b.household_id!=household_id: raise HTTPException(404,"Budget not found")
    q=select(func.coalesce(func.sum(Transaction.amount),0)).where(Transaction.household_id==household_id,Transaction.transaction_type=="expense",Transaction.transaction_date.between(b.period_start,b.period_end),Transaction.is_void.is_(False))
    if b.member_id:q=q.where(Transaction.member_id==b.member_id)
    if b.category_id:q=q.where(Transaction.category_id==b.category_id)
    actual=db.scalar(q) or 0; return {"planned":b.amount,"actual":actual,"remaining":b.amount-actual,"percent_used":actual/b.amount*100}
@router.post("/goals",response_model=GoalResponse,status_code=201)
def goal(household_id,p:GoalCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    auth(household_id,user,db); x=Goal(household_id=household_id,**p.model_dump()); db.add(x); db.flush(); return {**x.__dict__,"progress":x.current_amount/x.target_amount*100}
@router.get("/goals",response_model=list[GoalResponse])
def goals(household_id,user:User=Depends(current_user),db:Session=Depends(get_db)): auth(household_id,user,db); return db.scalars(select(Goal).where(Goal.household_id==household_id,Goal.is_active.is_(True))).all()
@router.post("/recurring",status_code=201)
def recurring(household_id,p:RecurringCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    auth(household_id,user,db); x=RecurringTransaction(household_id=household_id,**p.model_dump()); db.add(x); db.flush(); return {"id":x.id,"status":"scheduled"}
@router.get("/recurring")
def recurring_list(household_id,user:User=Depends(current_user),db:Session=Depends(get_db)): auth(household_id,user,db); return db.scalars(select(RecurringTransaction).where(RecurringTransaction.household_id==household_id,RecurringTransaction.is_active.is_(True))).all()
