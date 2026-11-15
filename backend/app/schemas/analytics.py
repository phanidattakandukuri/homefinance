from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel
class DashboardResponse(BaseModel):
    period_start: date; period_end: date; total_income: Decimal; total_expenses: Decimal; monthly_savings: Decimal; savings_rate: Decimal | None; total_investments: Decimal; total_assets: Decimal; total_liabilities: Decimal; net_worth: Decimal; monthly_cash_flow: Decimal; expense_categories: dict[str, Decimal]; member_totals: dict[str, dict[str, Decimal]]; investment_allocation: dict[str, Decimal]; pf_overview: dict[str, Decimal]
class SnapshotResponse(BaseModel):
    id: UUID; period_start: date; period_end: date; payload: dict; calculated_at: str
