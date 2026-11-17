"""complete typed household income and expense categories"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_14"
down_revision = "20261114_13"
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE transaction_categories SET category_type = CASE lower(name)
          WHEN 'salary' THEN 'income' WHEN 'freelance income' THEN 'income'
          WHEN 'interest' THEN 'income' WHEN 'dividends' THEN 'income'
          WHEN 'investments' THEN 'investment' WHEN 'transfers' THEN 'transfer'
          WHEN 'emi' THEN 'debt' ELSE category_type END
    """))
    rows = [
        ("00000000-0000-0000-0000-000000000029", "Investment returns", "income"),
        ("00000000-0000-0000-0000-000000000030", "Other income", "income"),
        ("00000000-0000-0000-0000-000000000031", "Business income", "income"),
        ("00000000-0000-0000-0000-000000000032", "Rental income", "income"),
        ("00000000-0000-0000-0000-000000000033", "Gifts received", "income"),
        ("00000000-0000-0000-0000-000000000034", "Electricity", "expense"),
        ("00000000-0000-0000-0000-000000000035", "Water", "expense"),
        ("00000000-0000-0000-0000-000000000036", "Fuel", "expense"),
        ("00000000-0000-0000-0000-000000000037", "Other expenses", "expense"),
    ]
    for identifier, name, category_type in rows:
        connection.execute(sa.text("""
            INSERT INTO transaction_categories (id, household_id, name, category_type, is_default, is_active)
            SELECT CAST(:id AS uuid), NULL, :name, :category_type, true, true
            WHERE NOT EXISTS (SELECT 1 FROM transaction_categories WHERE household_id IS NULL AND lower(name) = lower(:name))
        """), {"id": identifier, "name": name, "category_type": category_type})

def downgrade():
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM transaction_categories WHERE id::text BETWEEN '00000000-0000-0000-0000-000000000029' AND '00000000-0000-0000-0000-000000000037'"))
