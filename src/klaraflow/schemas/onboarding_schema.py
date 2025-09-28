from __future__ import annotations
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
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
    template_id: int | None = None  # Reference to onboarding template
    reportTo: str | None = None
    grade: str | None = None
    probationPeriod: str | None = None
    dateOfBirth: str | None = None
    maritalStatus: str | None = None
    nationality: str | None = None
    onboardingTemplateId: int | None = None

class OnboardingSessionRead(BaseModel):
    id: int
    company_id: int
    new_employee_email: EmailStr
    profilePic: Optional[str] = None
    firstName: str | None
    lastName: str | None
    empId: str | None
    status: str
    created_at: datetime
    expires_at: datetime
    current_step: int
    
    class Config:
        # Allow Pydantic to read attributes from ORM/SQLAlchemy model instances
        from_attributes = True
    
    
# Request model used when the invited user reviews and edits their information
class OnboardingReviewUpdateRequest(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    dateOfBirth: Optional[str] = None
    maritalStatus: Optional[str] = None
    nationality: Optional[str] = None
    # profile_picture will be uploaded via multipart/form-data as a file;
    # the router/CRUD will return the resulting URL in the response.


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
    status: str
    current_step: int

    class Config:
        from_attributes = True
        
class OnboardingActivationRequest(BaseModel):
    token: str
    password: str

class OnboardingStatusResponse(BaseModel):
    status: str
    current_step: int

class OnboardingStepUpdateRequest(BaseModel):
    current_step: int

# Todo Item Schemas
class TodoItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int = 0

class TodoItemCreate(TodoItemBase):
    pass

class TodoItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None

class TodoItemRead(TodoItemBase):
    id: int
    template_id: int
    created_at: datetime
    is_completed: bool = False

    class Config:
        from_attributes = True
        
class TodoItemStatusUpdate(BaseModel):
    completed: bool

# Onboarding Template Schemas
class OnboardingTemplateBase(BaseModel):
    name: str

class OnboardingTemplateCreate(OnboardingTemplateBase):
    todos: List[TodoItemCreate] = []
    required_document_ids: List[int] = []
    optional_document_ids: List[int] = []

class OnboardingTemplateUpdate(BaseModel):
    name: Optional[str] = None
    todos: Optional[List[TodoItemCreate]] = None
    required_document_ids: Optional[List[int]] = None
    optional_document_ids: Optional[List[int]] = None

class OnboardingTemplateRead(OnboardingTemplateBase):
    id: int
    company_id: int
    todos: List[TodoItemRead] = []
    required_documents: List["DocumentTemplateRead"] = []
    optional_documents: List["DocumentTemplateRead"] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Enhanced Onboarding Data (for frontend)
class OnboardingDocumentRead(BaseModel):
    id: int
    name: str
    fields: List[dict] = []
    required: bool = False
    uploaded: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OnboardingDataRead(BaseModel):
    # Minimal onboarding data returned to the user when fetching their onboarding info
    new_employee_email: EmailStr
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    empId: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    dateOfBirth: Optional[str] = None
    maritalStatus: Optional[str] = None
    nationality: Optional[str] = None
    profilePic: Optional[str] = None
    status: str
    current_step: int
    todos: List[TodoItemRead] = []
    required_documents: List[OnboardingDocumentRead] = []
    optional_documents: List[OnboardingDocumentRead] = []

    class Config:
        from_attributes = True

# Import DocumentTemplateRead for forward reference resolution
from klaraflow.schemas.document_schema import DocumentTemplateRead

# Rebuild model to resolve forward references after import
OnboardingTemplateRead.model_rebuild()