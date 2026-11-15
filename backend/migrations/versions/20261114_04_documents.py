"""create private document ingestion tables"""
from alembic import op
import sqlalchemy as sa
revision = "20261114_04"
down_revision = "20261114_03"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table("documents", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("household_id", sa.Uuid(), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False), sa.Column("uploaded_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False), sa.Column("member_id", sa.Uuid(), sa.ForeignKey("household_members.id", ondelete="SET NULL")), sa.Column("original_filename", sa.String(255), nullable=False), sa.Column("storage_key", sa.String(500), unique=True, nullable=False), sa.Column("mime_type", sa.String(100), nullable=False), sa.Column("extension", sa.String(10), nullable=False), sa.Column("size_bytes", sa.Integer(), nullable=False), sa.Column("document_type", sa.String(40), nullable=False, server_default="other"), sa.Column("status", sa.String(30), nullable=False, server_default="uploaded"), sa.Column("failure_reason", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_documents_household_id", "documents", ["household_id"])
    op.create_index("ix_documents_status", "documents", ["status"])
    op.create_table("document_extractions", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False), sa.Column("amount", sa.String(40)), sa.Column("transaction_date", sa.String(30)), sa.Column("merchant", sa.String(200)), sa.Column("payment_method", sa.String(60)), sa.Column("transaction_reference", sa.String(160)), sa.Column("sender_receiver", sa.String(300)), sa.Column("suggested_category", sa.String(100)), sa.Column("currency", sa.String(3)), sa.Column("confidence_score", sa.Float()), sa.Column("raw_extracted_text", sa.Text(), nullable=False), sa.Column("state", sa.String(30), nullable=False, server_default="awaiting_confirmation"), sa.Column("corrected_payload", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
def downgrade():
    op.drop_table("document_extractions")
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_index("ix_documents_household_id", table_name="documents")
    op.drop_table("documents")
