from pydantic import BaseModel, EmailStr
from datetime import datetime
from klaraflow.schemas.user_schema import Token

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
        
class OnboardingSessionDataResponse(BaseModel):
    new_employee_email: EmailStr
    firstName: str | None
    lastName: str | None
    empId: str | None
    phone: str | None
    gender: str | None
    userRole: str | None
    designation: str | None
    department: str | None
    jobType: str | None
    hiringDate: str | None
    reportTo: str | None
    grade: str | None
    probationPeriod: str | None
    dateOfBirth: str | None
    maritalStatus: str | None
    nationality: str | None

    class Config:
        from_attributes = True
        
class OnboardingActivationRequest(BaseModel):
    token: str
    password: str