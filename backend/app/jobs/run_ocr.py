"""Drain persisted OCR jobs from a trusted scheduler."""
from datetime import datetime, timezone
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.document import OCRJob
from app.api.v1.documents import process

def run(limit: int = 20) -> int:
    claimed = []
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        jobs = db.scalars(select(OCRJob).where(OCRJob.status.in_(["queued", "failed"]), OCRJob.available_at <= now).order_by(OCRJob.created_at).limit(limit)).all()
        for job in jobs:
            job.status = "claimed"; claimed.append((job.document_id, job.id))
        db.commit()
        for document_id, job_id in claimed:
            document = db.get(__import__("app.models.document", fromlist=["Document"]).Document, document_id)
            if document: process(document.id, document.storage_key, document.mime_type)
    return len(claimed)

if __name__ == "__main__":
    print(f"claimed_ocr_jobs={run()}")
