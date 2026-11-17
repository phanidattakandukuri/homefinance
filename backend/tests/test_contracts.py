from decimal import Decimal
from pydantic import ValidationError
import pytest
from app.schemas.notifications import NotificationPreferenceUpdate
from app.schemas.pf import PFEntryCreate

def test_pf_entry_accepts_separate_eps_component():
    entry = PFEntryCreate(entry_date="2026-01-01", entry_type="contribution", employee_contribution=Decimal("100"), employer_contribution=Decimal("100"), eps_contribution=Decimal("20"))
    assert entry.eps_contribution == Decimal("20")

def test_pf_entry_rejects_negative_eps():
    with pytest.raises(ValidationError):
        PFEntryCreate(entry_date="2026-01-01", entry_type="contribution", eps_contribution=-1)

def test_notification_channel_contract():
    item = NotificationPreferenceUpdate(channel="email")
    assert item.channel == "email"
