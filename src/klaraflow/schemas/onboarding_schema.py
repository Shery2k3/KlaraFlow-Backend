from pydantic import BaseModel, EmailStr
from datetime import datetime

# --- Onboarding Session Schemas ---

# Base properties shared by other schemas
class OnboardingSessionBase(BaseModel):
    new_employee_email: EmailStr

# Properties to receive via API on creation
class OnboardingSessionCreate(OnboardingSessionBase):
    pass

# Properties to return to client
class OnboardingSessionRead(OnboardingSessionBase):
    id: int
    company_id: int
    status: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True