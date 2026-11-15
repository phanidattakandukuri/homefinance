from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user, household_member
from app.db.session import get_db
from app.models.auth import User
from app.models.transaction import Category, Transaction, TransactionAudit
from app.schemas.transaction import CategoryCreate, CategoryResponse, DuplicateWarning, TransactionCreate, TransactionResponse, TransactionUpdate, TRANSACTION_TYPES

router = APIRouter(prefix="/households/{household_id}", tags=["transactions"])

def authorize(household_id, member_id, user, db):
    household_member(household_id, db, user)
    member = db.execute(select(__import__('app.models.household', fromlist=['HouseholdMember']).HouseholdMember).where(__import__('app.models.household', fromlist=['HouseholdMember']).HouseholdMember.id == member_id, __import__('app.models.household', fromlist=['HouseholdMember']).HouseholdMember.household_id == household_id)).scalar_one_or_none()
    if not member: raise HTTPException(404, "Member not found")

@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(household_id: UUID, payload: CategoryCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); category = Category(household_id=household_id, name=payload.name, parent_id=payload.parent_id); db.add(category); db.flush(); return category

@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); return db.scalars(select(Category).where(or_(Category.household_id == household_id, Category.is_default.is_(True)), Category.is_active.is_(True)).order_by(Category.name)).all()

@router.post("/transactions", response_model=TransactionResponse, status_code=201)
def create_transaction(household_id: UUID, payload: TransactionCreate, idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"), user: User = Depends(current_user), db: Session = Depends(get_db)):
    authorize(household_id, payload.member_id, user, db)
    if idempotency_key:
        existing = db.scalar(select(Transaction).where(Transaction.household_id == household_id, Transaction.idempotency_key == idempotency_key))
        if existing: return existing
    if payload.transaction_type not in TRANSACTION_TYPES: raise HTTPException(422, "Unsupported transaction type")
    category = db.get(Category, payload.category_id)
    if not category or (category.household_id not in (None, household_id) and not category.is_default): raise HTTPException(400, "Invalid category")
    transaction = Transaction(household_id=household_id, idempotency_key=idempotency_key, **payload.model_dump()); db.add(transaction); db.flush(); db.add(TransactionAudit(transaction_id=transaction.id, changed_by_user_id=user.id, action="created")); return transaction

def base_query(household_id, params, db):
    q = select(Transaction).where(Transaction.household_id == household_id, Transaction.is_void.is_(False))
    if params.get("member_id"): q = q.where(Transaction.member_id == params["member_id"])
    if params.get("category_id"): q = q.where(Transaction.category_id == params["category_id"])
    if params.get("transaction_type"): q = q.where(Transaction.transaction_type == params["transaction_type"])
    if params.get("start"): q = q.where(Transaction.transaction_date >= params["start"])
    if params.get("end"): q = q.where(Transaction.transaction_date <= params["end"])
    if params.get("search"):
        pattern = f"%{params['search']}%"; q = q.where(or_(Transaction.merchant.ilike(pattern), Transaction.description.ilike(pattern)))
    return q

@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(household_id: UUID, member_id: UUID | None = None, category_id: UUID | None = None, transaction_type: str | None = None, start: date | None = None, end: date | None = None, search: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200), user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); q = base_query(household_id, locals(), db).order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc()).offset((page-1)*page_size).limit(page_size); return db.scalars(q).all()

@router.patch("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(household_id: UUID, transaction_id: UUID, payload: TransactionUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); item = db.get(Transaction, transaction_id)
    if not item or item.household_id != household_id or item.is_void: raise HTTPException(404, "Transaction not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    db.add(TransactionAudit(transaction_id=item.id, changed_by_user_id=user.id, action="updated")); db.flush(); return item

@router.delete("/transactions/{transaction_id}", status_code=204)
def void_transaction(household_id: UUID, transaction_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); item = db.get(Transaction, transaction_id)
    if not item or item.household_id != household_id: raise HTTPException(404, "Transaction not found")
    item.is_void = True; db.add(TransactionAudit(transaction_id=item.id, changed_by_user_id=user.id, action="voided"))

@router.get("/transactions/{transaction_id}/duplicates", response_model=DuplicateWarning)
def duplicates(household_id: UUID, transaction_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); item = db.get(Transaction, transaction_id)
    if not item or item.household_id != household_id: raise HTTPException(404, "Transaction not found")
    q = select(Transaction).where(Transaction.household_id == household_id, Transaction.id != item.id, Transaction.is_void.is_(False), Transaction.member_id == item.member_id, Transaction.transaction_date == item.transaction_date, Transaction.amount == item.amount, Transaction.source == item.source, or_(and_(item.merchant.is_(None), Transaction.merchant.is_(None)), Transaction.merchant == item.merchant), or_(and_(item.reference_number.is_(None), Transaction.reference_number.is_(None)), Transaction.reference_number == item.reference_number))
    return {"possible_duplicates": db.scalars(q).all(), "warning": "Possible duplicate detected; no transaction was deleted automatically."}
