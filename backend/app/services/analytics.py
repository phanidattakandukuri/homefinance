from collections import defaultdict
from datetime import date
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.transaction import Transaction, Category
from app.models.wealth import Asset, Liability, Investment, InvestmentInstrument, InvestmentValuation
from app.models.household import HouseholdMember
from app.models.salary import SalaryRecord

INCOME = {"income", "interest", "dividend", "refund"}
EXPENSE = {"expense", "debt_payment", "adjustment"}
NON_CONSUMPTION = {"transfer", "investment_contribution", "investment_redemption"}
def dashboard(db: Session, household_id, start: date, end: date, member_id=None):
    q = select(Transaction, Category.name, HouseholdMember.display_name).join(Category, Transaction.category_id == Category.id).join(HouseholdMember, Transaction.member_id == HouseholdMember.id).where(Transaction.household_id == household_id, Transaction.transaction_date >= start, Transaction.transaction_date <= end, Transaction.is_void.is_(False))
    if member_id: q = q.where(Transaction.member_id == member_id)
    income=Decimal(0); expenses=Decimal(0); categories=defaultdict(Decimal); members=defaultdict(lambda: {"income": Decimal(0), "expenses": Decimal(0)})
    for tx, category, name in db.execute(q):
        if tx.transaction_type in INCOME: income += tx.amount
        elif tx.transaction_type in EXPENSE: expenses += tx.amount; categories[category] += tx.amount
        if tx.transaction_type in INCOME: members[name]["income"] += tx.amount
        elif tx.transaction_type in EXPENSE: members[name]["expenses"] += tx.amount
    assets = sum((x.current_value or 0 for x in db.scalars(select(Asset).where(Asset.household_id == household_id))), Decimal(0))
    liabilities = sum((x.current_outstanding or 0 for x in db.scalars(select(Liability).where(Liability.household_id == household_id))), Decimal(0))
    investments=Decimal(0); allocation=defaultdict(Decimal)
    for inv in db.scalars(select(Investment).where(Investment.household_id == household_id)):
        value = db.scalar(select(InvestmentValuation.current_value).where(InvestmentValuation.investment_id == inv.id).order_by(InvestmentValuation.valuation_date.desc()).limit(1)) or Decimal(0); investments += value
        instrument = db.get(InvestmentInstrument, inv.instrument_id)
        if instrument: allocation[instrument.category] += value
    savings=income-expenses; rate=(savings/income*100).quantize(Decimal("0.01")) if income else None
    pf=Decimal(0)
    for salary in db.scalars(select(SalaryRecord).where(SalaryRecord.household_id == household_id)):
        pf += salary.employee_pf or 0; pf += salary.employer_pf or 0
    return {"period_start":start,"period_end":end,"total_income":income,"total_expenses":expenses,"monthly_savings":savings,"savings_rate":rate,"total_investments":investments,"total_assets":assets,"total_liabilities":liabilities,"net_worth":assets+investments-liabilities,"monthly_cash_flow":income-expenses,"expense_categories":dict(categories),"member_totals":dict(members),"investment_allocation":dict(allocation),"pf_overview":{"employee_and_employer_contributions":pf}}
