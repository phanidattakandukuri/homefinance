from datetime import date
from pydantic import BaseModel, Field
class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    start: date | None = None
    end: date | None = None
class Evidence(BaseModel):
    tool: str
    date_range: str
    source: str
    data: dict
class AssistantResponse(BaseModel):
    answer: str
    evidence: list[Evidence]
    disclaimer: str = "This is an informational summary of recorded household data, not licensed financial advice."
