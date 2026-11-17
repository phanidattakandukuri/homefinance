"""add household member profile fields"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_10"
down_revision = "20261114_09"
branch_labels = None
depends_on = None


def upgrade():
    table = "household_members"
    op.add_column(table, sa.Column("email", sa.String(320), nullable=True))
    op.add_column(table, sa.Column("phone", sa.String(40), nullable=True))
    op.add_column(table, sa.Column("relationship_to_household", sa.String(80), nullable=True))
    op.add_column(table, sa.Column("employment_status", sa.String(40), nullable=True))
    op.add_column(table, sa.Column("occupation", sa.String(120), nullable=True))
    op.add_column(table, sa.Column("profile_image_url", sa.String(500), nullable=True))
    op.create_index("ix_household_members_email", table, ["email"])


def downgrade():
    table = "household_members"
    op.drop_index("ix_household_members_email", table_name=table)
    for column in ("profile_image_url", "occupation", "employment_status", "relationship_to_household", "phone", "email"):
        op.drop_column(table, column)
