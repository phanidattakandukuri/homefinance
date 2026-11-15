from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

class SalaryBase(BaseModel):
    employer_name: str | None = None
    designation: str | None = None
    salary_type: str = "annual_ctc"
    annual_ctc: Decimal | None = Field(default=None, ge=0)
    monthly_gross: Decimal | None = Field(default=None, ge=0)
    monthly_in_hand: Decimal | None = Field(default=None, ge=0)
    basic_salary: Decimal | None = Field(default=None, ge=0)
    hra: Decimal | None = Field(default=None, ge=0)
    special_allowance: Decimal | None = Field(default=None, ge=0)
    other_allowances: Decimal | None = Field(default=None, ge=0)
    employee_pf: Decimal | None = Field(default=None, ge=0)
    employer_pf: Decimal | None = Field(default=None, ge=0)
    professional_tax: Decimal | None = Field(default=None, ge=0)
    tds: Decimal | None = Field(default=None, ge=0)
    other_deductions: Decimal | None = Field(default=None, ge=0)
    gratuity_component: Decimal | None = Field(default=None, ge=0)
    effective_from: date
    effective_to: date | None = None

class SalaryCreate(SalaryBase): pass
class SalaryUpdate(BaseModel):
    employer_name: str | None = None
    designation: str | None = None
    effective_to: date | None = None

class SalaryResponse(SalaryBase):
    id: UUID
    household_id: UUID
    member_id: UUID
    model_config = {"from_attributes": True}

class SalaryBreakdown(BaseModel):
    salary_id: UUID
    monthly_gross: Decimal | None
    monthly_in_hand: Decimal | None
    monthly_employee_contributions: Decimal | None
    monthly_employer_contributions: Decimal | None
    monthly_deductions: Decimal | None
    calculation_note: str
