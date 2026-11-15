import io, re
from PIL import Image, ImageOps, ImageEnhance
try:
    import fitz
except ModuleNotFoundError:
    import pymupdf as fitz
import pytesseract
def image_text(data):
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(data))); image.thumbnail((2400, 2400)); image = ImageEnhance.Contrast(image.convert("L")).enhance(1.5); return pytesseract.image_to_string(image)
def pdf_text(data):
    doc = fitz.open(stream=data, filetype="pdf"); text = "\n".join(page.get_text() for page in doc)
    if text.strip(): return text
    return "\n".join(image_text(page.get_pixmap(matrix=fitz.Matrix(2, 2)).tobytes("png")) for page in doc)
def extract(data, mime): return pdf_text(data) if mime == "application/pdf" else image_text(data)
def structured(text, document_id):
    match = re.search(r"(?:INR|Rs\.?|₹|USD|\$)\s*([0-9,]+(?:\.\d{1,2})?)", text, re.I)
    return {"amount": match.group(1).replace(",", "") if match else None, "raw_extracted_text": text, "source_document_id": document_id, "confidence_score": 0.35 if text.strip() else 0.0, "currency": "INR" if re.search(r"INR|Rs\.?|₹", text, re.I) else None}
