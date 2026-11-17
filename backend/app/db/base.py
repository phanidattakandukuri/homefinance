from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

from app.models import auth, household, salary, transaction, document, wealth, analytics, planning, pf, notifications  # noqa: E402,F401
