from datetime import date
from calendar import monthrange
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

def advance(day: date, frequency: str) -> date:
    if frequency == "weekly": return date.fromordinal(day.toordinal() + 7)
    if frequency == "daily": return date.fromordinal(day.toordinal() + 1)
    if frequency in {"quarterly", "yearly", "annual", "monthly"}:
        months = 3 if frequency == "quarterly" else 12 if frequency in {"yearly", "annual"} else 1
        index = day.year * 12 + day.month - 1 + months
        year, month = divmod(index, 12); month += 1
        return date(year, month, min(day.day, monthrange(year, month)[1]))
    raise HTTPException(422, f"Unsupported recurring frequency: {frequency}")

@router.post("/recurring/run-due")
def run_due_recurring(household_id, as_of: date | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    auth(household_id,user,db); cutoff = as_of or date.today(); created = []
    for item in db.scalars(select(RecurringTransaction).where(RecurringTransaction.household_id == household_id, RecurringTransaction.is_active.is_(True), RecurringTransaction.next_run_date <= cutoff)).all():
        category = db.get(__import__('app.models.transaction', fromlist=['Category']).Category, item.category_id)
        if not category: continue
        while item.next_run_date <= cutoff:
            tx = Transaction(household_id=household_id, member_id=item.member_id, category_id=item.category_id, transaction_type=item.transaction_type, amount=item.amount, currency=(item.payload or {}).get("currency", "INR"), transaction_date=item.next_run_date, description=item.name, source="recurring", idempotency_key=f"recurring:{item.id}:{item.next_run_date.isoformat()}")
            db.add(tx); db.flush(); created.append(tx.id)
            item.next_run_date = advance(item.next_run_date, item.frequency)
    db.flush(); return {"created_transaction_ids": created, "count": len(created)}
