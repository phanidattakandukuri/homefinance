from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Household(Base):
    __tablename__ = "households"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200))
    base_currency: Mapped[str] = mapped_column(String(3), default="USD")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    members = relationship("HouseholdMember", back_populates="household", cascade="all, delete-orphan")


class HouseholdMember(Base):
    __tablename__ = "household_members"
    __table_args__ = (UniqueConstraint("household_id", "user_id", name="uq_household_user"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    household_id: Mapped[UUID] = mapped_column(ForeignKey("households.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    display_name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="member", index=True)
    membership_status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    household = relationship("Household", back_populates="members")
    user = relationship("User", back_populates="memberships")
