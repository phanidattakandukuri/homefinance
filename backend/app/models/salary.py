from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

MONEY = Numeric(14, 2)

class SalaryRecord(Base):
    __tablename__ = "salary_records"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    household_id: Mapped[UUID] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("household_members.id", ondelete="CASCADE"), index=True)
    employer_name: Mapped[str | None] = mapped_column(String(200))
    designation: Mapped[str | None] = mapped_column(String(200))
    salary_type: Mapped[str] = mapped_column(String(30), default="annual_ctc")
    annual_ctc: Mapped[Decimal | None] = mapped_column(MONEY)
    monthly_gross: Mapped[Decimal | None] = mapped_column(MONEY)
    monthly_in_hand: Mapped[Decimal | None] = mapped_column(MONEY)
    basic_salary: Mapped[Decimal | None] = mapped_column(MONEY)
    hra: Mapped[Decimal | None] = mapped_column(MONEY)
    special_allowance: Mapped[Decimal | None] = mapped_column(MONEY)
    other_allowances: Mapped[Decimal | None] = mapped_column(MONEY)
    employee_pf: Mapped[Decimal | None] = mapped_column(MONEY)
    employer_pf: Mapped[Decimal | None] = mapped_column(MONEY)
    professional_tax: Mapped[Decimal | None] = mapped_column(MONEY)
    tds: Mapped[Decimal | None] = mapped_column(MONEY)
    other_deductions: Mapped[Decimal | None] = mapped_column(MONEY)
    gratuity_component: Mapped[Decimal | None] = mapped_column(MONEY)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_to: Mapped[date | None] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    audit_events = relationship("SalaryAudit", back_populates="salary", cascade="all, delete-orphan")

class SalaryAudit(Base):
    __tablename__ = "salary_audits"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    salary_id: Mapped[UUID] = mapped_column(ForeignKey("salary_records.id", ondelete="CASCADE"), index=True)
    changed_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    action: Mapped[str] = mapped_column(String(30))
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    salary = relationship("SalaryRecord", back_populates="audit_events")
