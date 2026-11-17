"""add ownership and loan metadata to wealth records"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_11"
down_revision = "20261114_10"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("assets", sa.Column("ownership_percentage", sa.Numeric(5, 2), nullable=False, server_default="100"))
    op.add_column("assets", sa.Column("location", sa.String(300), nullable=True))
    op.add_column("liabilities", sa.Column("lender", sa.String(200), nullable=True))
    op.add_column("liabilities", sa.Column("interest_type", sa.String(20), nullable=False, server_default="fixed"))
    op.add_column("liabilities", sa.Column("emi_frequency", sa.String(20), nullable=False, server_default="monthly"))
    op.add_column("liabilities", sa.Column("next_emi_date", sa.Date(), nullable=True))
    op.add_column("liabilities", sa.Column("remaining_tenure_months", sa.Integer(), nullable=True))
    op.add_column("liabilities", sa.Column("associated_asset_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_liabilities_associated_asset", "liabilities", "assets", ["associated_asset_id"], ["id"], ondelete="SET NULL")

def downgrade():
    op.drop_constraint("fk_liabilities_associated_asset", "liabilities", type_="foreignkey")
    for column in ("associated_asset_id", "remaining_tenure_months", "next_emi_date", "emi_frequency", "interest_type", "lender"):
        op.drop_column("liabilities", column)
    op.drop_column("assets", "location")
    op.drop_column("assets", "ownership_percentage")
