from typing import Protocol
from app.core.config import get_settings
from app.models.auth import GeminiApiKey
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
import base64, hashlib
from cryptography.fernet import Fernet
from app.core.config import get_settings

def _cipher():
    secret = get_settings().app_secret_key.get_secret_value().encode()
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(secret).digest()))

def encrypt_key(value: str) -> str: return _cipher().encrypt(value.encode()).decode()
def decrypt_key(value: str) -> str: return _cipher().decrypt(value.encode()).decode()
class AIProvider(Protocol):
    def answer(self, question: str, context: list[dict]) -> str: ...
class GeminiProvider:
    def __init__(self, db: Session, user_id):
        settings = get_settings()
        key_row = db.scalar(select(GeminiApiKey).where(GeminiApiKey.user_id == user_id, GeminiApiKey.is_active.is_(True)).order_by(GeminiApiKey.created_at.desc()))
        raw_key = decrypt_key(key_row.encrypted_key) if key_row else (settings.gemini_api_key.get_secret_value() if settings.gemini_api_key else None)
        if not raw_key: raise RuntimeError("Gemini is not configured. Add a personal Gemini API key in Settings.")
        from google import genai
        self.client = genai.Client(api_key=raw_key); self.model = settings.gemini_model; self.db = db; self.key_row = key_row
    def answer(self, question, context):
        prompt = """You are HomeFin AI, a grounded household finance explainer. Use ONLY the VERIFIED DATA below. Never invent or infer missing figures. Say when data is unavailable. Do not give guaranteed returns or execute actions. Explain the date range and calculation when useful.\nVERIFIED DATA:\n""" + str(context) + "\nQUESTION:\n" + question
        answer = self.client.models.generate_content(model=self.model, contents=prompt).text
        if self.key_row:
            self.key_row.last_used_at = datetime.now(timezone.utc)
            self.db.flush()
        return answer
