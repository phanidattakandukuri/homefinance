"""persist household notification preferences"""
from alembic import op
import sqlalchemy as sa
revision = "20261114_19"; down_revision = "20261114_18"; branch_labels = None; depends_on = None
def upgrade():
    op.create_table("notification_preferences", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("household_id", sa.Uuid(), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("recurring_reminders", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("budget_alerts", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("goal_reminders", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("channel", sa.String(20), nullable=False, server_default="push"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("household_id", "user_id", name="uq_notification_preference"))
def downgrade(): op.drop_table("notification_preferences")
