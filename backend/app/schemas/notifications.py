from uuid import UUID
from pydantic import BaseModel
class NotificationPreferenceUpdate(BaseModel):
    enabled: bool = True; recurring_reminders: bool = True; budget_alerts: bool = True; goal_reminders: bool = True; channel: str = "push"
class NotificationPreferenceResponse(NotificationPreferenceUpdate):
    id: UUID; household_id: UUID; user_id: UUID
    model_config = {"from_attributes": True}
