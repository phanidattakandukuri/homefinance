import pytest
from pydantic import ValidationError

from app.schemas.transaction import TransactionCreate


def test_transaction_amount_must_be_positive() -> None:
    with pytest.raises(ValidationError, match="greater than 0"):
        TransactionCreate(
            member_id="00000000-0000-0000-0000-000000000001",
            category_id="00000000-0000-0000-0000-000000000002",
            transaction_type="expense",
            amount="0",
            transaction_date="2026-11-16",
        )


def test_transaction_type_is_restricted() -> None:
    with pytest.raises(ValidationError, match="Unsupported transaction type"):
        TransactionCreate(
            member_id="00000000-0000-0000-0000-000000000001",
            category_id="00000000-0000-0000-0000-000000000002",
            transaction_type="salary",
            amount="100",
            transaction_date="2026-11-16",
        )


def test_transaction_amount_accepts_display_formatting() -> None:
    payload = TransactionCreate(
        member_id="00000000-0000-0000-0000-000000000001",
        category_id="00000000-0000-0000-0000-000000000002",
        transaction_type="expense",
        amount="₹24,457",
        transaction_date="2026-11-16",
    )

    assert str(payload.amount) == "24457"

def test_transaction_amount_is_always_positive() -> None:
    with pytest.raises(ValidationError):
        TransactionCreate(
            member_id="00000000-0000-0000-0000-000000000001",
            category_id="00000000-0000-0000-0000-000000000002",
            transaction_type="income",
            amount="-1",
            transaction_date="2026-11-16",
        )
