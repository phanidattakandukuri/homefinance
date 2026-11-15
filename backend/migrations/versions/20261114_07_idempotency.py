"""add transaction idempotency keys"""
from alembic import op
import sqlalchemy as sa
revision="20261114_07"; down_revision="20261114_06"; branch_labels=None; depends_on=None
def upgrade():
    op.add_column("transactions", sa.Column("idempotency_key", sa.String(120)))
    op.create_index("ix_transactions_idempotency_key", "transactions", ["idempotency_key"])
    op.create_unique_constraint("uq_transaction_household_idempotency", "transactions", ["household_id", "idempotency_key"])
def downgrade():
    op.drop_constraint("uq_transaction_household_idempotency", "transactions", type_="unique"); op.drop_index("ix_transactions_idempotency_key", table_name="transactions"); op.drop_column("transactions", "idempotency_key")
