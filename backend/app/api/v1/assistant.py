from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user, household_member
from app.db.session import get_db
from app.models.auth import User
from app.schemas.assistant import AssistantRequest, AssistantResponse, Evidence
from app.services.ai_provider import GeminiProvider
from app.services.assistant_tools import get_household_summary, get_investment_summary, get_pf_summary, get_net_worth
router=APIRouter(prefix="/households/{household_id}/assistant",tags=["assistant"])
@router.post("/ask",response_model=AssistantResponse)
def ask(household_id, payload:AssistantRequest, user:User=Depends(current_user), db:Session=Depends(get_db)):
    household_member(household_id,db,user)
    if any(x in payload.question.lower() for x in ("ignore previous", "system prompt", "reveal prompt", "invent", "make up")): raise HTTPException(400,"The assistant only answers from verified household data")
    start=payload.start; end=payload.end; context=[]
    summary=get_household_summary(db,household_id,start,end); context.append({"tool":"get_household_summary","data":summary,"date_range":f"{start or 'current month'} to {end or date.today()}"})
    q=payload.question.lower()
    if any(x in q for x in ("invest", "wealth", "retire", "afford", "recommend", "suggest", "portfolio", "risk", "financial plan")):
        context.append({"tool":"get_investment_summary","data":get_investment_summary(db,household_id),"date_range":"latest dated valuation","source":"investment_valuations"})
        context.append({"tool":"get_pf_summary","data":get_pf_summary(db,household_id),"date_range":"all recorded salary contributions","source":"salary_records"})
        context.append({"tool":"get_net_worth","data":get_net_worth(db,household_id,start,end),"date_range":f"{start or 'current'} to {end or date.today()}","source":"analytics aggregation"})
    if "net worth" in q: context.append({"tool":"get_net_worth","data":get_net_worth(db,household_id,start,end),"date_range":f"{start or 'current'} to {end or date.today()}","source":"analytics aggregation"})
    try: answer=GeminiProvider(db, user.id).answer(payload.question,context)
    except RuntimeError: answer="Gemini is not configured. Verified data is available in the evidence below; no unverified answer was generated."
    evidence=[Evidence(tool=x["tool"],date_range=x.get("date_range","requested period"),source=x.get("source","authoritative analytics aggregation"),data=x["data"]) for x in context]
    return {"answer":answer,"evidence":evidence}
