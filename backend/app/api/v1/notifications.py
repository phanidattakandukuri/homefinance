from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.dependencies import current_user, household_member
from app.db.session import get_db
from app.models.auth import User
from app.models.notifications import NotificationPreference
from app.schemas.notifications import NotificationPreferenceResponse, NotificationPreferenceUpdate
router = APIRouter(prefix="/households/{household_id}/notifications", tags=["notifications"])
@router.get("/preferences", response_model=NotificationPreferenceResponse)
def get_preferences(household_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user); item = db.scalar(select(NotificationPreference).where(NotificationPreference.household_id == household_id, NotificationPreference.user_id == user.id))
    if not item: item = NotificationPreference(household_id=household_id, user_id=user.id); db.add(item); db.flush()
    return item
@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_preferences(household_id: UUID, payload: NotificationPreferenceUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    household_member(household_id, db, user)
    if payload.channel not in {"push", "email", "none"}: raise HTTPException(422, "channel must be push, email, or none")
    item = db.scalar(select(NotificationPreference).where(NotificationPreference.household_id == household_id, NotificationPreference.user_id == user.id))
    if not item: item = NotificationPreference(household_id=household_id, user_id=user.id); db.add(item)
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.flush(); return item
