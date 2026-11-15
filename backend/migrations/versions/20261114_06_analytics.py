"""create financial snapshots"""
from alembic import op
import sqlalchemy as sa
revision="20261114_06"; down_revision="20261114_05"; branch_labels=None; depends_on=None
def upgrade():
    u=sa.Uuid(); op.create_table("financial_snapshots",sa.Column("id",u,primary_key=True),sa.Column("household_id",u,sa.ForeignKey("households.id",ondelete="CASCADE"),nullable=False),sa.Column("period_start",sa.Date(),nullable=False),sa.Column("period_end",sa.Date(),nullable=False),sa.Column("payload",sa.JSON(),nullable=False),sa.Column("calculated_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("recalculation_reason",sa.String(300)),sa.UniqueConstraint("household_id","period_start","period_end",name="uq_snapshot_period")); op.create_index("ix_financial_snapshots_household_id","financial_snapshots",["household_id"])
    op.create_table("snapshot_audits",sa.Column("id",u,primary_key=True),sa.Column("snapshot_id",u,sa.ForeignKey("financial_snapshots.id",ondelete="CASCADE"),nullable=False),sa.Column("action",sa.String(30),nullable=False),sa.Column("reason",sa.String(300),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
def downgrade():
    op.drop_table("snapshot_audits"); op.drop_index("ix_financial_snapshots_household_id",table_name="financial_snapshots"); op.drop_table("financial_snapshots")
