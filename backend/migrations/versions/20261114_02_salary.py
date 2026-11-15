"""create salary records and audit history"""
from alembic import op
import sqlalchemy as sa
revision = "20261114_02"
down_revision = "20261114_01"
branch_labels = None
depends_on = None

def upgrade():
    money = sa.Numeric(14, 2)
    op.create_table("salary_records",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("household_id", sa.Uuid(), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False), sa.Column("member_id", sa.Uuid(), sa.ForeignKey("household_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employer_name", sa.String(200)), sa.Column("designation", sa.String(200)), sa.Column("salary_type", sa.String(30), nullable=False, server_default="annual_ctc"),
        *[sa.Column(n, money) for n in ("annual_ctc","monthly_gross","monthly_in_hand","basic_salary","hra","special_allowance","other_allowances","employee_pf","employer_pf","professional_tax","tds","other_deductions","gratuity_component")],
        sa.Column("effective_from", sa.Date(), nullable=False), sa.Column("effective_to", sa.Date()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_salary_records_household_id", "salary_records", ["household_id"]); op.create_index("ix_salary_records_member_id", "salary_records", ["member_id"]); op.create_index("ix_salary_records_effective_from", "salary_records", ["effective_from"])
    op.create_table("salary_audits", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("salary_id", sa.Uuid(), sa.ForeignKey("salary_records.id", ondelete="CASCADE"), nullable=False), sa.Column("changed_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False), sa.Column("action", sa.String(30), nullable=False), sa.Column("details", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_salary_audits_salary_id", "salary_audits", ["salary_id"])

def downgrade():
    op.drop_table("salary_audits"); op.drop_index("ix_salary_records_effective_from", table_name="salary_records"); op.drop_index("ix_salary_records_member_id", table_name="salary_records"); op.drop_index("ix_salary_records_household_id", table_name="salary_records"); op.drop_table("salary_records")
