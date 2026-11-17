from datetime import date
from decimal import Decimal
from app.services.finance import emi_schedule, xirr

def test_xirr_returns_annualized_result_for_irregular_flows():
    result = xirr([(date(2025, 1, 1), Decimal("-1000")), (date(2025, 7, 1), Decimal("1000")), (date(2026, 1, 1), Decimal("1100"))])
    assert result is not None
    assert result > Decimal("0.09")

def test_emi_schedule_separates_principal_and_interest():
    schedule = emi_schedule(Decimal("100000"), Decimal("12"), Decimal("5000"), 30)
    assert schedule[0]["interest"] == Decimal("1000.00")
    assert schedule[0]["principal"] == Decimal("4000.00")
    assert schedule[-1]["balance"] == Decimal("0")
