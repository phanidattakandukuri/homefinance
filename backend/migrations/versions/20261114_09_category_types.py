"""classify transaction categories for mobile validation"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_09"
down_revision = "20261114_08"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("transaction_categories", sa.Column("category_type", sa.String(20), nullable=False, server_default="expense"))
    op.create_index("ix_transaction_categories_category_type", "transaction_categories", ["category_type"])
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE transaction_categories SET category_type = 'income' "
            "WHERE lower(name) IN ('salary', 'freelance income', 'interest', 'dividends')"
        )
    )
    connection.execute(
        sa.text(
            "UPDATE transaction_categories SET category_type = 'transfer' "
            "WHERE lower(name) IN ('transfers', 'transfer')"
        )
    )
    connection.execute(
        sa.text(
            "UPDATE transaction_categories SET category_type = 'investment' "
            "WHERE lower(name) IN ('investments', 'investment')"
        )
    )
    connection.execute(
        sa.text(
            "INSERT INTO transaction_categories (id, household_id, name, category_type, is_default, is_active) "
            "VALUES "
            "('00000000-0000-0000-0000-000000000019', NULL, 'Business income', 'income', true, true),"
            "('00000000-0000-0000-0000-000000000020', NULL, 'Rental income', 'income', true, true),"
            "('00000000-0000-0000-0000-000000000021', NULL, 'Gifts received', 'income', true, true),"
            "('00000000-0000-0000-0000-000000000022', NULL, 'Other income', 'income', true, true),"
            "('00000000-0000-0000-0000-000000000023', NULL, 'Electricity', 'expense', true, true),"
            "('00000000-0000-0000-0000-000000000024', NULL, 'Water', 'expense', true, true),"
            "('00000000-0000-0000-0000-000000000025', NULL, 'Fuel', 'expense', true, true),"
            "('00000000-0000-0000-0000-000000000026', NULL, 'Loan EMI', 'debt', true, true),"
            "('00000000-0000-0000-0000-000000000027', NULL, 'Credit card payment', 'debt', true, true),"
            "('00000000-0000-0000-0000-000000000028', NULL, 'Other expenses', 'expense', true, true)"
        )
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM transaction_categories WHERE id::text IN ('00000000-0000-0000-0000-000000000019','00000000-0000-0000-0000-000000000020','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000022','00000000-0000-0000-0000-000000000023','00000000-0000-0000-0000-000000000024','00000000-0000-0000-0000-000000000025','00000000-0000-0000-0000-000000000026','00000000-0000-0000-0000-000000000027','00000000-0000-0000-0000-000000000028')"))
    op.drop_index("ix_transaction_categories_category_type", table_name="transaction_categories")
    op.drop_column("transaction_categories", "category_type")
