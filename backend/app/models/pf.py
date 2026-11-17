from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

MONEY = Numeric(16, 2)

class ProvidentFundAccount(Base):
    __tablename__ = "provident_fund_accounts"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    household_id: Mapped[UUID] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("household_members.id", ondelete="CASCADE"), index=True)
    scheme: Mapped[str] = mapped_column(String(20), default="EPF")
    opening_balance: Mapped[Decimal] = mapped_column(MONEY, default=0)
    current_balance: Mapped[Decimal | None] = mapped_column(MONEY)
    interest_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ProvidentFundEntry(Base):
    __tablename__ = "provident_fund_entries"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("provident_fund_accounts.id", ondelete="CASCADE"), index=True)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    entry_type: Mapped[str] = mapped_column(String(30))
    employee_contribution: Mapped[Decimal] = mapped_column(MONEY, default=0)
    employer_contribution: Mapped[Decimal] = mapped_column(MONEY, default=0)
    eps_contribution: Mapped[Decimal] = mapped_column(MONEY, default=0)
    interest_credited: Mapped[Decimal] = mapped_column(MONEY, default=0)
    withdrawal: Mapped[Decimal] = mapped_column(MONEY, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

class GratuityProfile(Base):
    __tablename__ = "gratuity_profiles"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    household_id: Mapped[UUID] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("household_members.id", ondelete="CASCADE"), index=True)
    joining_date: Mapped[date] = mapped_column(Date)
    basic_salary: Mapped[Decimal] = mapped_column(MONEY)
    da_salary: Mapped[Decimal] = mapped_column(MONEY, default=0)
    estimated_amount: Mapped[Decimal | None] = mapped_column(MONEY)
    actual_received: Mapped[Decimal | None] = mapped_column(MONEY)
    notes: Mapped[str | None] = mapped_column(Text)
