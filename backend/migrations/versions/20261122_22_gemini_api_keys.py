"""add per-user Gemini API keys"""
from alembic import op
import sqlalchemy as sa
revision = "20261122_22"
down_revision = "20261114_21"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table("gemini_api_keys", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("label", sa.String(100), nullable=False, server_default="Gemini key"), sa.Column("encrypted_key", sa.Text(), nullable=False), sa.Column("last_four", sa.String(4), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("last_used_at", sa.DateTime(timezone=True)))
    op.create_index("ix_gemini_api_keys_user_id", "gemini_api_keys", ["user_id"])
def downgrade():
    op.drop_index("ix_gemini_api_keys_user_id", table_name="gemini_api_keys")
    op.drop_table("gemini_api_keys")
