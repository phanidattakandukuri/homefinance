"""create users, households, and household memberships

Revision ID: 20261114_01
"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_01"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("email"))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("households",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("name", sa.String(200), nullable=False),
        sa.Column("base_currency", sa.String(3), nullable=False, server_default="USD"), sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("household_members",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("household_id", sa.Uuid(), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE")), sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="member"), sa.Column("membership_status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.UniqueConstraint("household_id", "user_id", name="uq_household_user"))
    op.create_index("ix_household_members_household_id", "household_members", ["household_id"])
    op.create_index("ix_household_members_user_id", "household_members", ["user_id"])
    op.create_index("ix_household_members_role", "household_members", ["role"])
    op.create_index("ix_household_members_membership_status", "household_members", ["membership_status"])

def downgrade() -> None:
    op.drop_table("household_members"); op.drop_table("households"); op.drop_index("ix_users_email", table_name="users"); op.drop_table("users")
