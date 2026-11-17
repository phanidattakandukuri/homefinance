"""persist OCR processing jobs"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_17"
down_revision = "20261114_16"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("ocr_jobs", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True), sa.Column("status", sa.String(20), nullable=False, server_default="queued"), sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"), sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("started_at", sa.DateTime(timezone=True)), sa.Column("completed_at", sa.DateTime(timezone=True)), sa.Column("last_error", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_ocr_jobs_document_id", "ocr_jobs", ["document_id"])
    op.create_index("ix_ocr_jobs_status", "ocr_jobs", ["status"])
    op.create_index("ix_ocr_jobs_available_at", "ocr_jobs", ["available_at"])

def downgrade():
    op.drop_table("ocr_jobs")
