from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
class InstrumentCreate(BaseModel): name: str; category: str; identifier: str | None = None; currency: str = "INR"
class InstrumentResponse(InstrumentCreate): id: UUID; model_config = {"from_attributes": True}
class InvestmentCreate(BaseModel): member_id: UUID; instrument_id: UUID; notes: str | None = None
class InvestmentResponse(InvestmentCreate): id: UUID; household_id: UUID; model_config = {"from_attributes": True}
class InvestmentTransactionCreate(BaseModel): transaction_type: str; quantity: Decimal | None = None; unit_price: Decimal | None = None; fees: Decimal = Field(default=0, ge=0); cash_flow: Decimal; transaction_date: date; source_document_id: UUID | None = None; notes: str | None = None
class ValuationCreate(BaseModel): valuation_date: date; quantity: Decimal | None = None; unit_price: Decimal | None = None; current_value: Decimal; source: str = "manual"; notes: str | None = None
class AssetCreate(BaseModel): member_id: UUID | None = None; name: str; category: str; acquisition_cost: Decimal | None = None; current_value: Decimal | None = None; acquisition_date: date | None = None; valuation_date: date | None = None; notes: str | None = None
class LiabilityCreate(BaseModel): member_id: UUID | None = None; name: str; category: str; original_principal: Decimal | None = None; current_outstanding: Decimal | None = None; interest_rate: Decimal | None = None; emi: Decimal | None = None; start_date: date | None = None; end_date: date | None = None; notes: str | None = None
class WealthResponse(BaseModel): id: UUID; model_config = {"from_attributes": True}
