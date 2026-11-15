from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.services.analytics import dashboard
from app.models.household import HouseholdMember
from app.models.wealth import Investment, InvestmentValuation, InvestmentInstrument
from app.models.salary import SalaryRecord
from sqlalchemy import select
def date_range(start=None, end=None):
    end = end or date.today(); start = start or end.replace(day=1); return start, end
def get_household_summary(db: Session, household_id, start=None, end=None): return dashboard(db, household_id, *date_range(start,end))
def get_member_summary(db: Session, household_id, member_id, start=None, end=None): return dashboard(db, household_id, *date_range(start,end), member_id)
def get_monthly_income(db, household_id, start=None, end=None): return {"total_income": get_household_summary(db,household_id,start,end)["total_income"]}
def get_monthly_expenses(db, household_id, start=None, end=None): return {"total_expenses": get_household_summary(db,household_id,start,end)["total_expenses"]}
def get_expense_breakdown(db, household_id, start=None, end=None): return {"expense_categories": get_household_summary(db,household_id,start,end)["expense_categories"]}
def get_investment_summary(db, household_id):
    values=[]
    for inv in db.scalars(select(Investment).where(Investment.household_id==household_id)):
        value=db.scalar(select(InvestmentValuation.current_value).where(InvestmentValuation.investment_id==inv.id).order_by(InvestmentValuation.valuation_date.desc()).limit(1)); values.append(value or Decimal(0))
    return {"total_investments":sum(values,Decimal(0)),"valuation_is_dated":True}
def get_pf_summary(db, household_id):
    employee=sum((x.employee_pf or 0 for x in db.scalars(select(SalaryRecord).where(SalaryRecord.household_id==household_id))),Decimal(0)); employer=sum((x.employer_pf or 0 for x in db.scalars(select(SalaryRecord).where(SalaryRecord.household_id==household_id))),Decimal(0)); return {"employee_contributions":employee,"employer_contributions":employer,"note":"Contribution records only; EPS and current PF balance require confirmed passbook data."}
def get_net_worth(db, household_id, start=None, end=None):
    result=get_household_summary(db,household_id,start,end); return {"net_worth":result["net_worth"],"source":"dated assets, investment valuations, and liability records"}
TOOL_REGISTRY={"get_household_summary":get_household_summary,"get_member_summary":get_member_summary,"get_monthly_income":get_monthly_income,"get_monthly_expenses":get_monthly_expenses,"get_expense_breakdown":get_expense_breakdown,"get_investment_summary":get_investment_summary,"get_pf_summary":get_pf_summary,"get_net_worth":get_net_worth}
