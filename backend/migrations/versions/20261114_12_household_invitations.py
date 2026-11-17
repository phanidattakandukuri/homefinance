"""add expiring household invitations"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_12"
down_revision = "20261114_11"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("household_invitations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("household_id", sa.Uuid(), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("member_id", sa.Uuid(), sa.ForeignKey("household_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("invited_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    for name in ("household_id", "member_id", "token_hash", "expires_at"):
        op.create_index(f"ix_household_invitations_{name}", "household_invitations", [name])

def downgrade():
    op.drop_table("household_invitations")
