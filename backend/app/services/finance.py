from datetime import date
from decimal import Decimal, getcontext

getcontext().prec = 28

def xirr(cash_flows: list[tuple[date, Decimal]], guess: Decimal = Decimal("0.1")) -> Decimal | None:
    """Return annualized XIRR for dated cash flows, or None when unsolvable.

    Contributions are negative and proceeds/valuations are positive. This is
    intentionally pure and uses Decimal arithmetic for reproducible reports.
    """
    if len(cash_flows) < 2 or not any(amount < 0 for _, amount in cash_flows) or not any(amount > 0 for _, amount in cash_flows):
        return None
    origin = min(day for day, _ in cash_flows)
    def value(rate: Decimal) -> Decimal:
        return sum((amount / (Decimal(1) + rate) ** (Decimal((day - origin).days) / Decimal("365")) for day, amount in cash_flows), Decimal(0))
    def derivative(rate: Decimal) -> Decimal:
        result = Decimal(0)
        for day, amount in cash_flows:
            years = Decimal((day - origin).days) / Decimal("365")
            result -= years * amount / (Decimal(1) + rate) ** (years + 1)
        return result
    rate = max(Decimal("-0.99"), guess)
    for _ in range(100):
        current = value(rate); slope = derivative(rate)
        if abs(current) < Decimal("0.000001"): return rate
        if slope == 0: return None
        next_rate = rate - current / slope
        if next_rate <= Decimal("-0.999999") or next_rate > Decimal("1000"): return None
        if abs(next_rate - rate) < Decimal("0.00000001"): return next_rate
        rate = next_rate
    return None

def emi_schedule(principal: Decimal, annual_rate_percent: Decimal, monthly_payment: Decimal, payments: int) -> list[dict[str, Decimal | int]]:
    """Build a fixed-rate amortization schedule with explicit principal/interest."""
    if principal <= 0 or monthly_payment <= 0 or payments <= 0: raise ValueError("principal, payment, and payments must be positive")
    monthly_rate = annual_rate_percent / Decimal("1200")
    balance = principal
    schedule = []
    for number in range(1, payments + 1):
        interest = (balance * monthly_rate).quantize(Decimal("0.01"))
        principal_paid = min(balance, monthly_payment - interest) if monthly_payment > interest else Decimal(0)
        balance = max(Decimal(0), balance - principal_paid)
        schedule.append({"payment_number": number, "payment": principal_paid + interest, "principal": principal_paid, "interest": interest, "balance": balance})
        if balance == 0: break
    return schedule
