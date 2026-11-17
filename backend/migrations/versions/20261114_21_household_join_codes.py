"""add expiring household join codes"""
from alembic import op
import sqlalchemy as sa
revision = "20261114_21"; down_revision = "20261114_20"; branch_labels = None; depends_on = None
def upgrade():
    op.create_table("household_join_codes", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("household_id", sa.Uuid(), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False), sa.Column("created_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False), sa.Column("code_hash", sa.String(64), nullable=False, unique=True), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("revoked_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_household_join_codes_household_id", "household_join_codes", ["household_id"])
    op.create_index("ix_household_join_codes_code_hash", "household_join_codes", ["code_hash"])
    op.create_index("ix_household_join_codes_expires_at", "household_join_codes", ["expires_at"])
def downgrade(): op.drop_table("household_join_codes")
