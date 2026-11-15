from uuid import UUID
from pydantic import BaseModel, Field

class HouseholdCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    base_currency: str = Field(default="USD", min_length=3, max_length=3)
    timezone: str = "UTC"
    earning_member_names: list[str] = Field(default_factory=list, max_length=3)

class HouseholdUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    base_currency: str | None = Field(default=None, min_length=3, max_length=3)
    timezone: str | None = None

class MemberCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    user_id: UUID | None = None
    role: str = "member"

class MemberRoleUpdate(BaseModel):
    role: str

class MemberResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    display_name: str
    role: str
    membership_status: str
    model_config = {"from_attributes": True}

class HouseholdResponse(BaseModel):
    id: UUID
    name: str
    base_currency: str
    timezone: str
    members: list[MemberResponse] = []
    model_config = {"from_attributes": True}
