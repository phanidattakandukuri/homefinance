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
    email: str | None = None
    phone: str | None = None
    relationship_to_household: str | None = None
    employment_status: str | None = None
    occupation: str | None = None
    profile_image_url: str | None = None
    role: str = "member"

class MemberUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=200)
    email: str | None = None
    phone: str | None = None
    relationship_to_household: str | None = None
    employment_status: str | None = None
    occupation: str | None = None
    profile_image_url: str | None = None
    role: str | None = None
    membership_status: str | None = None

class MemberResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    display_name: str
    email: str | None
    phone: str | None
    relationship_to_household: str | None
    employment_status: str | None
    occupation: str | None
    profile_image_url: str | None
    role: str
    membership_status: str
    model_config = {"from_attributes": True}

class InvitationCreate(BaseModel):
    email: str
    display_name: str = Field(min_length=1, max_length=200)
    role: str = "member"
    relationship_to_household: str | None = None

class InvitationResponse(BaseModel):
    invitation_id: UUID
    member_id: UUID
    email: str
    expires_at: str
    invitation_token: str

class HouseholdResponse(BaseModel):
    id: UUID
    name: str
    base_currency: str
    timezone: str
    members: list[MemberResponse] = []
    model_config = {"from_attributes": True}
