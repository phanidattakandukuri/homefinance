"""add server-side JWT token versioning"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_15"
down_revision = "20261114_14"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))

def downgrade():
    op.drop_column("users", "token_version")
