from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
MONEY = Numeric(16, 2)
UNITS = Numeric(20, 8)

class InvestmentInstrument(Base):
    __tablename__ = "investment_instruments"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    household_id: Mapped[UUID] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200)); category: Mapped[str] = mapped_column(String(40), index=True)
    identifier: Mapped[str | None] = mapped_column(String(100)); currency: Mapped[str] = mapped_column(String(3), default="INR")

class Investment(Base):
    __tablename__ = "investments"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    household_id: Mapped[UUID] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("household_members.id", ondelete="RESTRICT"), index=True)
    instrument_id: Mapped[UUID] = mapped_column(ForeignKey("investment_instruments.id", ondelete="RESTRICT"))
    notes: Mapped[str | None] = mapped_column(Text)

class InvestmentTransaction(Base):
    __tablename__ = "investment_transactions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    investment_id: Mapped[UUID] = mapped_column(ForeignKey("investments.id", ondelete="CASCADE"), index=True)
    transaction_type: Mapped[str] = mapped_column(String(35), index=True)
    quantity: Mapped[Decimal | None] = mapped_column(UNITS); unit_price: Mapped[Decimal | None] = mapped_column(MONEY)
    fees: Mapped[Decimal] = mapped_column(MONEY, default=0); cash_flow: Mapped[Decimal] = mapped_column(MONEY)
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    source_document_id: Mapped[UUID | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"))
    notes: Mapped[str | None] = mapped_column(Text)

class InvestmentValuation(Base):
    __tablename__ = "investment_valuations"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    investment_id: Mapped[UUID] = mapped_column(ForeignKey("investments.id", ondelete="CASCADE"), index=True)
    valuation_date: Mapped[date] = mapped_column(Date, index=True); quantity: Mapped[Decimal | None] = mapped_column(UNITS)
    unit_price: Mapped[Decimal | None] = mapped_column(MONEY); current_value: Mapped[Decimal] = mapped_column(MONEY)
    source: Mapped[str] = mapped_column(String(30), default="manual"); notes: Mapped[str | None] = mapped_column(Text)

class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4); household_id: Mapped[UUID] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True); member_id: Mapped[UUID | None] = mapped_column(ForeignKey("household_members.id", ondelete="SET NULL")); name: Mapped[str] = mapped_column(String(200)); category: Mapped[str] = mapped_column(String(40)); acquisition_cost: Mapped[Decimal | None] = mapped_column(MONEY); current_value: Mapped[Decimal | None] = mapped_column(MONEY); ownership_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=100); acquisition_date: Mapped[date | None] = mapped_column(Date); valuation_date: Mapped[date | None] = mapped_column(Date); location: Mapped[str | None] = mapped_column(String(300)); notes: Mapped[str | None] = mapped_column(Text)

class Liability(Base):
    __tablename__ = "liabilities"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4); household_id: Mapped[UUID] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True); member_id: Mapped[UUID | None] = mapped_column(ForeignKey("household_members.id", ondelete="SET NULL")); name: Mapped[str] = mapped_column(String(200)); category: Mapped[str] = mapped_column(String(40)); lender: Mapped[str | None] = mapped_column(String(200)); original_principal: Mapped[Decimal | None] = mapped_column(MONEY); current_outstanding: Mapped[Decimal | None] = mapped_column(MONEY); interest_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 4)); interest_type: Mapped[str] = mapped_column(String(20), default="fixed"); emi: Mapped[Decimal | None] = mapped_column(MONEY); emi_frequency: Mapped[str] = mapped_column(String(20), default="monthly"); start_date: Mapped[date | None] = mapped_column(Date); end_date: Mapped[date | None] = mapped_column(Date); next_emi_date: Mapped[date | None] = mapped_column(Date); remaining_tenure_months: Mapped[int | None] = mapped_column(); associated_asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("assets.id", ondelete="SET NULL")); notes: Mapped[str | None] = mapped_column(Text)

class LiabilityPayment(Base):
    __tablename__ = "liability_payments"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4); liability_id: Mapped[UUID] = mapped_column(ForeignKey("liabilities.id", ondelete="CASCADE"), index=True); payment_date: Mapped[date] = mapped_column(Date); amount: Mapped[Decimal] = mapped_column(MONEY); principal: Mapped[Decimal | None] = mapped_column(MONEY); interest: Mapped[Decimal | None] = mapped_column(MONEY); notes: Mapped[str | None] = mapped_column(Text)
