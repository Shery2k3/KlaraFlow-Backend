from pydantic import BaseModel, EmailStr
from datetime import datetime

class OnboardingInviteRequest(BaseModel):
    # Mandatory fields from FE
    empId: str
    firstName: str
    lastName: str
    email: EmailStr
    gender: str
    userRole: str
    
    # Optional fields from FE
    phone: str | None = None
    designation: str | None = None
    department: str | None = None
    jobType: str | None = None
    hiringDate: str | None = None
    onboardingTemplateId: str | None = None
    reportTo: str | None = None
    grade: str | None = None
    probationPeriod: str | None = None
    dateOfBirth: str | None = None
    maritalStatus: str | None = None
    nationality: str | None = None

class OnboardingSessionRead(BaseModel):
    id: int
    company_id: int
    new_employee_email: EmailStr
    status: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True