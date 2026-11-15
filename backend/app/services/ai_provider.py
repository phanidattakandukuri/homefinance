from typing import Protocol
from app.core.config import get_settings
class AIProvider(Protocol):
    def answer(self, question: str, context: list[dict]) -> str: ...
class GeminiProvider:
    def __init__(self):
        settings = get_settings()
        if not settings.gemini_api_key: raise RuntimeError("GEMINI_API_KEY is not configured")
        from google import genai
        self.client = genai.Client(api_key=settings.gemini_api_key.get_secret_value()); self.model = settings.gemini_model
    def answer(self, question, context):
        prompt = """You are HomeFin AI, a grounded household finance explainer. Use ONLY the VERIFIED DATA below. Never invent or infer missing figures. Say when data is unavailable. Do not give guaranteed returns or execute actions. Explain the date range and calculation when useful.\nVERIFIED DATA:\n""" + str(context) + "\nQUESTION:\n" + question
        return self.client.models.generate_content(model=self.model, contents=prompt).text
