"""add manual PF and gratuity ledgers"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_13"
down_revision = "20261114_12"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("provident_fund_accounts", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("household_id", sa.Uuid(), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False), sa.Column("member_id", sa.Uuid(), sa.ForeignKey("household_members.id", ondelete="CASCADE"), nullable=False), sa.Column("scheme", sa.String(20), nullable=False), sa.Column("opening_balance", sa.Numeric(16,2), nullable=False), sa.Column("current_balance", sa.Numeric(16,2)), sa.Column("interest_rate", sa.Numeric(8,4)), sa.Column("notes", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("provident_fund_entries", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("account_id", sa.Uuid(), sa.ForeignKey("provident_fund_accounts.id", ondelete="CASCADE"), nullable=False), sa.Column("entry_date", sa.Date(), nullable=False), sa.Column("entry_type", sa.String(30), nullable=False), sa.Column("employee_contribution", sa.Numeric(16,2), nullable=False), sa.Column("employer_contribution", sa.Numeric(16,2), nullable=False), sa.Column("interest_credited", sa.Numeric(16,2), nullable=False), sa.Column("withdrawal", sa.Numeric(16,2), nullable=False), sa.Column("notes", sa.Text()))
    op.create_table("gratuity_profiles", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("household_id", sa.Uuid(), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False), sa.Column("member_id", sa.Uuid(), sa.ForeignKey("household_members.id", ondelete="CASCADE"), nullable=False), sa.Column("joining_date", sa.Date(), nullable=False), sa.Column("basic_salary", sa.Numeric(16,2), nullable=False), sa.Column("da_salary", sa.Numeric(16,2), nullable=False), sa.Column("estimated_amount", sa.Numeric(16,2)), sa.Column("actual_received", sa.Numeric(16,2)), sa.Column("notes", sa.Text()))
    for table, column in (("provident_fund_accounts", "household_id"), ("provident_fund_accounts", "member_id"), ("provident_fund_entries", "account_id"), ("gratuity_profiles", "household_id"), ("gratuity_profiles", "member_id")):
        op.create_index(f"ix_{table}_{column}", table, [column])

def downgrade():
    op.drop_table("gratuity_profiles")
    op.drop_table("provident_fund_entries")
    op.drop_table("provident_fund_accounts")
