from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator

CATEGORY_TYPES = {"income", "expense", "transfer", "investment", "debt", "other"}
TRANSACTION_TYPES = {"income", "expense", "transfer", "investment_contribution", "investment_redemption", "debt_payment", "refund", "interest", "dividend", "adjustment"}

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category_type: str = Field(default="expense", pattern="^(income|expense|transfer|investment|debt|other)$")
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

    @field_validator("amount", mode="before")
    @classmethod
    def normalize_amount(cls, value: object) -> object:
        if isinstance(value, str):
            return value.replace(",", "").replace(" ", "").replace("₹", "").replace("$", "").replace("€", "").replace("£", "")
        return value

    @model_validator(mode="after")
    def validate_transaction(self):
        if self.transaction_type not in TRANSACTION_TYPES:
            raise ValueError("Unsupported transaction type")
        if self.amount <= 0:
            raise ValueError("Amount must be greater than zero")
        if self.currency != self.currency.upper():
            raise ValueError("Currency must use uppercase ISO format")
        return self

class TransferCreate(BaseModel):
    from_member_id: UUID
    to_member_id: UUID
    category_id: UUID
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    transaction_date: date
    description: str | None = None
    notes: str | None = None

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

class TransactionAuditResponse(BaseModel):
    id: UUID
    transaction_id: UUID
    changed_by_user_id: UUID
    action: str
    details: str | None
    created_at: str
    model_config = {"from_attributes": True}
