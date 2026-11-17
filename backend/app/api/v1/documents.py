import io
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user, household_member
from app.core.config import get_settings
from app.db.session import get_db, SessionLocal
from app.models.auth import User
from app.models.document import Document, Extraction, OCRJob
from app.schemas.document import ConfirmationResponse, DocumentResponse, ExtractionCorrection, ExtractionResult, OCRJobResponse
from app.services.ocr import extract, structured
from app.services.storage import storage
router = APIRouter(prefix="/households/{household_id}/documents", tags=["documents"])
ALLOWED = {"image/png": ".png", "image/jpeg": ".jpg", "application/pdf": ".pdf", "image/webp": ".webp"}
MAGIC = {".png": b"\x89PNG", ".jpg": b"\xff\xd8\xff", ".pdf": b"%PDF", ".webp": b"RIFF"}
def process(document_id, key, mime):
    db = SessionLocal(); document = db.get(Document, document_id)
    job = db.scalar(select(OCRJob).where(OCRJob.document_id == document_id))
    try:
        if not document or not job: return
        job.status = "processing"; job.attempts += 1; job.started_at = datetime.now(timezone.utc); document.status = "processing"; db.commit()
        with storage().open(key) as f: text = extract(f.read(), mime)
        values = structured(text, document_id); values.pop("source_document_id", None)
        db.add(Extraction(document_id=document_id, **{k: str(v) if v is not None else None for k, v in values.items()})); document.status = "awaiting_confirmation"; db.commit()
        job.status = "completed"; job.completed_at = datetime.now(timezone.utc); job.last_error = None; db.commit()
    except Exception as exc:
        if job:
            job.status = "failed"; job.last_error = str(exc)[:500]; job.available_at = datetime.now(timezone.utc) + timedelta(minutes=min(60, 2 ** min(job.attempts, 5)))
        document.status = "failed"; document.failure_reason = str(exc)[:500]; db.commit()
    finally: db.close()
@router.post("", response_model=DocumentResponse, status_code=201)
async def upload(household_id: UUID, background: BackgroundTasks, file: UploadFile = File(...), document_type: str = "other", user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); suffix = ALLOWED.get(file.content_type or "")
    if not suffix: raise HTTPException(415, "Unsupported document type")
    data = await file.read()
    if len(data) > get_settings().max_upload_size_mb * 1024 * 1024: raise HTTPException(413, "File is too large")
    if not data.startswith(MAGIC[suffix]): raise HTTPException(415, "File signature does not match MIME type")
    key = f"{household_id}/{uuid4().hex}{suffix}"; storage().save(io.BytesIO(data), key)
    document = Document(household_id=household_id, uploaded_by_user_id=user.id, original_filename=(file.filename or "document")[:255], storage_key=key, mime_type=file.content_type, extension=suffix, size_bytes=len(data), document_type=document_type); db.add(document); db.flush()
    job = OCRJob(document_id=document.id); db.add(job); db.flush(); background.add_task(process, document.id, key, file.content_type); return document
def owned(household_id, document_id, user, db):
    household_member(household_id, db, user); document = db.get(Document, document_id)
    if not document or document.household_id != household_id: raise HTTPException(404, "Document not found")
    return document
@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(household_id: UUID, document_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)): return owned(household_id, document_id, user, db)
@router.get("/{document_id}/extraction", response_model=ExtractionResult)
def get_extraction(household_id: UUID, document_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    owned(household_id, document_id, user, db); extraction = db.query(Extraction).filter_by(document_id=document_id).one_or_none()
    if not extraction: raise HTTPException(404, "Extraction not available")
    return {**extraction.__dict__, "source_document_id": document_id}
@router.post("/{document_id}/confirm", response_model=ConfirmationResponse)
def confirm(household_id: UUID, document_id: UUID, correction: ExtractionCorrection, user: User = Depends(current_user), db: Session = Depends(get_db)):
    document = owned(household_id, document_id, user, db); extraction = db.query(Extraction).filter_by(document_id=document_id).one_or_none()
    if not extraction: raise HTTPException(404, "Extraction not available")
    extraction.corrected_payload = correction.model_dump_json(); extraction.state = "confirmed"; document.status = "confirmed"; return {"document_id": document_id, "status": "confirmed", "transaction_id": None}
@router.post("/{document_id}/reject", response_model=ConfirmationResponse)
def reject(household_id: UUID, document_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    document = owned(household_id, document_id, user, db); document.status = "rejected"; extraction = db.query(Extraction).filter_by(document_id=document_id).one_or_none()
    if extraction: extraction.state = "rejected"
    return {"document_id": document_id, "status": "rejected", "transaction_id": None}

@router.get("/{document_id}/ocr-job", response_model=OCRJobResponse)
def ocr_job(household_id: UUID, document_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    owned(household_id, document_id, user, db)
    job = db.scalar(select(OCRJob).where(OCRJob.document_id == document_id))
    if not job: raise HTTPException(404, "OCR job not found")
    return job

@router.post("/{document_id}/ocr-job/retry", response_model=OCRJobResponse)
def retry_ocr(household_id: UUID, document_id: UUID, background: BackgroundTasks, user: User = Depends(current_user), db: Session = Depends(get_db)):
    document = owned(household_id, document_id, user, db)
    job = db.scalar(select(OCRJob).where(OCRJob.document_id == document_id))
    if not job: raise HTTPException(404, "OCR job not found")
    if job.status == "processing": raise HTTPException(409, "OCR job is already processing")
    job.status = "queued"; job.last_error = None; document.status = "uploaded"; db.flush(); background.add_task(process, document.id, document.storage_key, document.mime_type); return job
