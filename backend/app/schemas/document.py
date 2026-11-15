from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
class ExtractionResult(BaseModel):
    amount: Decimal | None = None; transaction_date: date | None = None; merchant: str | None = None; payment_method: str | None = None; transaction_reference: str | None = None; sender_receiver: str | None = None; suggested_category: str | None = None; currency: str | None = None; confidence_score: float | None = Field(default=None, ge=0, le=1); raw_extracted_text: str; source_document_id: UUID
class DocumentResponse(BaseModel):
    id: UUID; original_filename: str; mime_type: str; size_bytes: int; document_type: str; status: str
    model_config = {"from_attributes": True}
class ExtractionCorrection(BaseModel):
    amount: Decimal | None = None; transaction_date: date | None = None; merchant: str | None = None; member_id: UUID | None = None; category_id: UUID | None = None
class ConfirmationResponse(BaseModel):
    document_id: UUID; status: str; transaction_id: UUID | None = None
