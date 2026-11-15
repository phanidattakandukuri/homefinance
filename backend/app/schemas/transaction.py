from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

TRANSACTION_TYPES = {"income", "expense", "transfer", "investment_contribution", "investment_redemption", "debt_payment", "refund", "interest", "dividend", "adjustment"}

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    parent_id: UUID | None = None

class CategoryResponse(CategoryCreate):
    id: UUID
    model_config = {"from_attributes": True}

class TransactionCreate(BaseModel):
    member_id: UUID
    account_id: UUID | None = None
    transaction_type: str
    category_id: UUID
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    transaction_date: date
    description: str | None = None
    merchant: str | None = None
    payment_method: str | None = None
    notes: str | None = None
    source: str | None = None
    reference_number: str | None = None
    linked_transaction_id: UUID | None = None

class TransactionUpdate(BaseModel):
    category_id: UUID | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    transaction_date: date | None = None
    description: str | None = None
    merchant: str | None = None
    notes: str | None = None
    reference_number: str | None = None

class TransactionResponse(TransactionCreate):
    id: UUID
    household_id: UUID
    is_void: bool
    model_config = {"from_attributes": True}

class DuplicateWarning(BaseModel):
    possible_duplicates: list[TransactionResponse]
    warning: str
