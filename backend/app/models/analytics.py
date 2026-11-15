from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Date, DateTime, ForeignKey, JSON, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class FinancialSnapshot(Base):
    __tablename__ = "financial_snapshots"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    household_id: Mapped[UUID] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True)
    period_start: Mapped[date] = mapped_column(Date); period_end: Mapped[date] = mapped_column(Date)
    payload: Mapped[dict] = mapped_column(JSON); calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    recalculation_reason: Mapped[str | None] = mapped_column(String(300))
    __table_args__ = (UniqueConstraint("household_id", "period_start", "period_end", name="uq_snapshot_period"),)
class SnapshotAudit(Base):
    __tablename__ = "snapshot_audits"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4); snapshot_id: Mapped[UUID] = mapped_column(ForeignKey("financial_snapshots.id", ondelete="CASCADE")); action: Mapped[str] = mapped_column(String(30)); reason: Mapped[str] = mapped_column(String(300)); created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
