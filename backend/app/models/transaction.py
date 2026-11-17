from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Category(Base):
    __tablename__ = "transaction_categories"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    household_id: Mapped[UUID | None] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    category_type: Mapped[str] = mapped_column(String(20), default="expense", index=True)
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("transaction_categories.id", ondelete="CASCADE"))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    __table_args__ = (UniqueConstraint("household_id", "name", "parent_id", name="uq_category_scope_name_parent"),)

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("household_id", "idempotency_key", name="uq_transaction_household_idempotency"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    household_id: Mapped[UUID] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("household_members.id", ondelete="RESTRICT"), index=True)
    account_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    transaction_type: Mapped[str] = mapped_column(String(40), index=True)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("transaction_categories.id", ondelete="RESTRICT"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    merchant: Mapped[str | None] = mapped_column(String(200), index=True)
    payment_method: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(50), index=True)
    reference_number: Mapped[str | None] = mapped_column(String(120), index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), index=True)
    is_void: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    linked_transaction_id: Mapped[UUID | None] = mapped_column(ForeignKey("transactions.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TransactionAudit(Base):
    __tablename__ = "transaction_audits"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    transaction_id: Mapped[UUID] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"), index=True)
    changed_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    action: Mapped[str] = mapped_column(String(30))
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
