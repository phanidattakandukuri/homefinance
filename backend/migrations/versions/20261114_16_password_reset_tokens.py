"""add expiring password reset tokens"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_16"
down_revision = "20261114_15"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("password_reset_tokens", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("token_hash", sa.String(64), nullable=False, unique=True), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("used_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    for column in ("user_id", "token_hash", "expires_at"):
        op.create_index(f"ix_password_reset_tokens_{column}", "password_reset_tokens", [column])

def downgrade():
    op.drop_table("password_reset_tokens")
