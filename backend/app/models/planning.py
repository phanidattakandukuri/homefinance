from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class Budget(Base):
    __tablename__="budgets"
    id:Mapped[UUID]=mapped_column(primary_key=True,default=uuid4); household_id:Mapped[UUID]=mapped_column(ForeignKey("households.id",ondelete="CASCADE"),index=True); member_id:Mapped[UUID|None]=mapped_column(ForeignKey("household_members.id",ondelete="CASCADE")); category_id:Mapped[UUID|None]=mapped_column(ForeignKey("transaction_categories.id",ondelete="CASCADE")); name:Mapped[str]=mapped_column(String(150)); amount:Mapped[Decimal]=mapped_column(Numeric(14,2)); period_start:Mapped[date]=mapped_column(Date); period_end:Mapped[date]=mapped_column(Date); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class Goal(Base):
    __tablename__="financial_goals"
    id:Mapped[UUID]=mapped_column(primary_key=True,default=uuid4); household_id:Mapped[UUID]=mapped_column(ForeignKey("households.id",ondelete="CASCADE"),index=True); member_id:Mapped[UUID|None]=mapped_column(ForeignKey("household_members.id",ondelete="CASCADE")); name:Mapped[str]=mapped_column(String(150)); goal_type:Mapped[str]=mapped_column(String(40)); target_amount:Mapped[Decimal]=mapped_column(Numeric(14,2)); target_date:Mapped[date|None]=mapped_column(Date); current_amount:Mapped[Decimal]=mapped_column(Numeric(14,2),default=0); is_active:Mapped[bool]=mapped_column(Boolean,default=True)
class RecurringTransaction(Base):
    __tablename__="recurring_transactions"
    id:Mapped[UUID]=mapped_column(primary_key=True,default=uuid4); household_id:Mapped[UUID]=mapped_column(ForeignKey("households.id",ondelete="CASCADE"),index=True); member_id:Mapped[UUID]=mapped_column(ForeignKey("household_members.id",ondelete="RESTRICT")); category_id:Mapped[UUID]=mapped_column(ForeignKey("transaction_categories.id",ondelete="RESTRICT")); name:Mapped[str]=mapped_column(String(150)); transaction_type:Mapped[str]=mapped_column(String(30)); amount:Mapped[Decimal]=mapped_column(Numeric(14,2)); frequency:Mapped[str]=mapped_column(String(20)); next_run_date:Mapped[date]=mapped_column(Date); is_active:Mapped[bool]=mapped_column(Boolean,default=True); last_generated_key:Mapped[str|None]=mapped_column(String(100)); payload:Mapped[dict|None]=mapped_column(JSON)
