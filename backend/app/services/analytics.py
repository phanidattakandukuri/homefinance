from collections import defaultdict
from datetime import date
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.transaction import Transaction, Category
from app.models.wealth import Asset, Liability, Investment, InvestmentInstrument, InvestmentValuation
from app.models.household import HouseholdMember
from app.models.salary import SalaryRecord
from app.models.pf import ProvidentFundAccount, ProvidentFundEntry, GratuityProfile

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
    asset_query = select(Asset).where(Asset.household_id == household_id)
    liability_query = select(Liability).where(Liability.household_id == household_id)
    if member_id:
        asset_query = asset_query.where(Asset.member_id == member_id)
        liability_query = liability_query.where(Liability.member_id == member_id)
    assets = sum(((x.current_value or Decimal(0)) * (x.ownership_percentage or Decimal(100)) / Decimal(100) for x in db.scalars(asset_query)), Decimal(0))
    liabilities = sum((x.current_outstanding or Decimal(0) for x in db.scalars(liability_query)), Decimal(0))
    investments=Decimal(0); allocation=defaultdict(Decimal)
    investment_query = select(Investment).where(Investment.household_id == household_id)
    if member_id: investment_query = investment_query.where(Investment.member_id == member_id)
    for inv in db.scalars(investment_query):
        value = db.scalar(select(InvestmentValuation.current_value).where(InvestmentValuation.investment_id == inv.id).order_by(InvestmentValuation.valuation_date.desc()).limit(1)) or Decimal(0); investments += value
        instrument = db.get(InvestmentInstrument, inv.instrument_id)
        if instrument: allocation[instrument.category] += value
    savings=income-expenses; rate=(savings/income*100).quantize(Decimal("0.01")) if income else None
    salary_pf=Decimal(0); pf_balance=Decimal(0); epf_balance=Decimal(0); eps_balance=Decimal(0); gratuity=Decimal(0)
    salary_query = select(SalaryRecord).where(SalaryRecord.household_id == household_id)
    if member_id: salary_query = salary_query.where(SalaryRecord.member_id == member_id)
    for salary in db.scalars(salary_query):
        salary_pf += salary.employee_pf or 0; salary_pf += salary.employer_pf or 0
    pf_query = select(ProvidentFundAccount).where(ProvidentFundAccount.household_id == household_id)
    gratuity_query = select(GratuityProfile).where(GratuityProfile.household_id == household_id)
    if member_id:
        pf_query = pf_query.where(ProvidentFundAccount.member_id == member_id)
        gratuity_query = gratuity_query.where(GratuityProfile.member_id == member_id)
    for account in db.scalars(pf_query):
        entries = db.scalars(select(ProvidentFundEntry).where(ProvidentFundEntry.account_id == account.id))
        calculated = account.opening_balance + sum((x.employee_contribution + x.employer_contribution + x.interest_credited - x.withdrawal for x in entries), Decimal(0))
        epf = account.current_balance if account.current_balance is not None and account.scheme.upper() == "EPF" else calculated
        eps = sum((x.eps_contribution for x in entries), Decimal(0))
        if account.scheme.upper() == "EPS": eps += account.current_balance or account.opening_balance
        if account.scheme.upper() == "COMBINED": epf = calculated - eps
        epf_balance += epf; eps_balance += eps; pf_balance += epf + eps
    gratuity = sum((x.estimated_amount or Decimal(0) for x in db.scalars(gratuity_query)), Decimal(0))
    return {"period_start":start,"period_end":end,"total_income":income,"total_expenses":expenses,"monthly_savings":savings,"savings_rate":rate,"total_investments":investments,"total_assets":assets,"total_liabilities":liabilities,"net_worth":assets+investments-liabilities,"monthly_cash_flow":income-expenses,"expense_categories":dict(categories),"member_totals":dict(members),"investment_allocation":dict(allocation),"pf_overview":{"salary_contributions":salary_pf,"recorded_balance":pf_balance,"epf_balance":epf_balance,"eps_balance":eps_balance,"estimated_gratuity":gratuity}}
