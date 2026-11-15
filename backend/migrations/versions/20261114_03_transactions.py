"""create categories, transactions, and transaction audit"""
from alembic import op
import sqlalchemy as sa
revision = "20261114_03"
down_revision = "20261114_02"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("transaction_categories", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("household_id", sa.Uuid(), sa.ForeignKey("households.id", ondelete="CASCADE")), sa.Column("name", sa.String(100), nullable=False), sa.Column("parent_id", sa.Uuid(), sa.ForeignKey("transaction_categories.id", ondelete="CASCADE")), sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.UniqueConstraint("household_id", "name", "parent_id", name="uq_category_scope_name_parent"))
    op.create_index("ix_transaction_categories_household_id", "transaction_categories", ["household_id"])
    defaults = ["Food", "Groceries", "Rent", "Utilities", "Transport", "Healthcare", "Education", "Shopping", "Entertainment", "Insurance", "EMI", "Salary", "Freelance income", "Interest", "Dividends", "Investments", "Transfers"]
    op.bulk_insert(sa.table("transaction_categories", sa.column("id", sa.Uuid()), sa.column("name", sa.String()), sa.column("is_default", sa.Boolean()), sa.column("is_active", sa.Boolean())), [{"id": f"00000000-0000-0000-0000-{i:012d}", "name": name, "is_default": True, "is_active": True} for i, name in enumerate(defaults, 1)])
    op.create_table("transactions", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("household_id", sa.Uuid(), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False), sa.Column("member_id", sa.Uuid(), sa.ForeignKey("household_members.id", ondelete="RESTRICT"), nullable=False), sa.Column("account_id", sa.Uuid()), sa.Column("transaction_type", sa.String(40), nullable=False), sa.Column("category_id", sa.Uuid(), sa.ForeignKey("transaction_categories.id", ondelete="RESTRICT"), nullable=False), sa.Column("amount", sa.Numeric(14,2), nullable=False), sa.Column("currency", sa.String(3), nullable=False, server_default="USD"), sa.Column("transaction_date", sa.Date(), nullable=False), sa.Column("description", sa.Text()), sa.Column("merchant", sa.String(200)), sa.Column("payment_method", sa.String(40)), sa.Column("notes", sa.Text()), sa.Column("source", sa.String(50)), sa.Column("reference_number", sa.String(120)), sa.Column("is_void", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("linked_transaction_id", sa.Uuid(), sa.ForeignKey("transactions.id", ondelete="SET NULL")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    for column in ("household_id","member_id","account_id","transaction_type","category_id","transaction_date","merchant","source","reference_number","is_void"): op.create_index(f"ix_transactions_{column}", "transactions", [column])
    op.create_table("transaction_audits", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("transaction_id", sa.Uuid(), sa.ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False), sa.Column("changed_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False), sa.Column("action", sa.String(30), nullable=False), sa.Column("details", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_transaction_audits_transaction_id", "transaction_audits", ["transaction_id"])

def downgrade():
    op.drop_table("transaction_audits")
    for column in ("household_id","member_id","account_id","transaction_type","category_id","transaction_date","merchant","source","reference_number","is_void"): op.drop_index(f"ix_transactions_{column}", table_name="transactions")
    op.drop_table("transactions"); op.drop_index("ix_transaction_categories_household_id", table_name="transaction_categories"); op.drop_table("transaction_categories")
