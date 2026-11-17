"""add server-side JWT token versioning"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_15"
down_revision = "20261114_14"
branch_labels = None
depends_on = None

def upgrade():
    op.execute(
        "ALTER TABLE users "
        "ADD COLUMN IF NOT EXISTS token_version INTEGER NOT NULL DEFAULT 0"
    )

def downgrade():
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS token_version")
