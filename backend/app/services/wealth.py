from decimal import Decimal
def investment_totals(transactions, valuation=None):
    invested = sum((t.cash_flow for t in transactions if t.transaction_type in {"buy", "sip_contribution", "deposit", "investment_contribution"}), Decimal("0"))
    proceeds = sum((t.cash_flow for t in transactions if t.transaction_type in {"sell", "withdrawal", "maturity", "investment_redemption"}), Decimal("0"))
    dividends = sum((t.cash_flow for t in transactions if t.transaction_type == "dividend"), Decimal("0"))
    interest = sum((t.cash_flow for t in transactions if t.transaction_type == "interest"), Decimal("0"))
    current = valuation.current_value if valuation else None
    return {"invested_amount": invested, "current_value": current, "realized_gain_loss": proceeds + dividends + interest - invested, "unrealized_gain_loss": current - invested if current is not None else None, "dividends": dividends, "interest": interest, "absolute_return": (current + proceeds + dividends + interest - invested) if current is not None else None}
def net_worth(asset_values, investment_values, liability_values):
    return sum(asset_values, Decimal("0")) + sum(investment_values, Decimal("0")) - sum(liability_values, Decimal("0"))
