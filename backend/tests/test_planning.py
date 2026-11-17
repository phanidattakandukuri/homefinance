from datetime import date
import pytest
from fastapi import HTTPException
from app.api.v1.planning import advance

def test_advance_supported_frequencies():
    assert advance(date(2026, 1, 31), "monthly") == date(2026, 2, 28)
    assert advance(date(2026, 1, 1), "weekly") == date(2026, 1, 8)
    assert advance(date(2026, 1, 1), "quarterly") == date(2026, 4, 1)
    assert advance(date(2026, 1, 1), "annual") == date(2027, 1, 1)

def test_advance_rejects_unknown_frequency():
    with pytest.raises(HTTPException) as error:
        advance(date(2026, 1, 1), "fortnightly")
    assert error.value.status_code == 422
