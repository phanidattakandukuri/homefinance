"""store EPS pension contribution separately from EPF"""
from alembic import op
import sqlalchemy as sa
revision = "20261114_18"
down_revision = "20261114_17"
branch_labels = None
depends_on = None
def upgrade():
    op.add_column("provident_fund_entries", sa.Column("eps_contribution", sa.Numeric(16, 2), nullable=False, server_default="0"))
def downgrade():
    op.drop_column("provident_fund_entries", "eps_contribution")
