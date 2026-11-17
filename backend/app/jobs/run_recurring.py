"""Generate due recurring transactions for every household."""
from datetime import date
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.household import Household
from app.models.planning import RecurringTransaction
from app.models.transaction import Category, Transaction
from app.api.v1.planning import advance

def run(as_of: date | None = None) -> int:
    cutoff = as_of or date.today(); count = 0
    with SessionLocal() as db:
        for household in db.scalars(select(Household)):
            items = db.scalars(select(RecurringTransaction).where(RecurringTransaction.household_id == household.id, RecurringTransaction.is_active.is_(True), RecurringTransaction.next_run_date <= cutoff)).all()
            for item in items:
                if not db.get(Category, item.category_id): continue
                while item.next_run_date <= cutoff:
                    db.add(Transaction(household_id=household.id, member_id=item.member_id, category_id=item.category_id, transaction_type=item.transaction_type, amount=item.amount, currency=(item.payload or {}).get("currency", household.base_currency), transaction_date=item.next_run_date, description=item.name, source="recurring", idempotency_key=f"recurring:{item.id}:{item.next_run_date.isoformat()}"))
                    item.next_run_date = advance(item.next_run_date, item.frequency); count += 1
        db.commit()
    return count

if __name__ == "__main__":
    print(f"created_recurring_transactions={run()}")
