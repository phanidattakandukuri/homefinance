from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

class PFAccountCreate(BaseModel):
    member_id: UUID
    scheme: str = "EPF"
    opening_balance: Decimal = Field(default=0, ge=0)
    current_balance: Decimal | None = Field(default=None, ge=0)
    interest_rate: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None

class PFAccountResponse(PFAccountCreate):
    id: UUID
    household_id: UUID
    model_config = {"from_attributes": True}

class PFEntryCreate(BaseModel):
    entry_date: date
    entry_type: str
    employee_contribution: Decimal = Field(default=0, ge=0)
    employer_contribution: Decimal = Field(default=0, ge=0)
    eps_contribution: Decimal = Field(default=0, ge=0)
    interest_credited: Decimal = Field(default=0, ge=0)
    withdrawal: Decimal = Field(default=0, ge=0)
    notes: str | None = None

class PFEntryResponse(PFEntryCreate):
    id: UUID
    account_id: UUID
    model_config = {"from_attributes": True}

class GratuityCreate(BaseModel):
    member_id: UUID
    joining_date: date
    basic_salary: Decimal = Field(gt=0)
    da_salary: Decimal = Field(default=0, ge=0)
    actual_received: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None

class GratuityResponse(GratuityCreate):
    id: UUID
    household_id: UUID
    estimated_amount: Decimal | None
    model_config = {"from_attributes": True}
