from pydantic import BaseModel, EmailStr
from datetime import datetime

class OnboardingInviteRequest(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    phone: str | None = None
    gender: str
    userRole: str
    designation: str | None = None
    department: str | None = None
    onboardingTemplateId: str
    

class OnboardingSessionRead(BaseModel):
    id: int
    company_id: int
    new_employee_email: EmailStr
    status: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True