from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class FieldTypeEnum(str, Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    FILE = "file"
    DATE = "date"

class FieldWidthEnum(str, Enum):
    HALF = "half"
    FULL = "full"

# Document Field Schemas
class DocumentFieldBase(BaseModel):
    label: str
    field_type: FieldTypeEnum = Field(alias="type")
    placeholder: Optional[str] = None  
    description: Optional[str] = None
    required: bool = False
    width: FieldWidthEnum = FieldWidthEnum.FULL
    order_index: int = 0

class DocumentFieldCreate(DocumentFieldBase):
    pass

class DocumentFieldUpdate(BaseModel):
    label: Optional[str] = None
    field_type: Optional[FieldTypeEnum] = Field(None, alias="type")
    placeholder: Optional[str] = None
    description: Optional[str] = None
    required: Optional[bool] = None
    width: Optional[FieldWidthEnum] = None
    order_index: Optional[int] = None

class DocumentFieldRead(DocumentFieldBase):
    id: int
    template_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

# Document Template Schemas
class DocumentTemplateBase(BaseModel):
    name: str

class DocumentTemplateCreate(DocumentTemplateBase):
    fields: List[DocumentFieldCreate] = []

class DocumentTemplateUpdate(BaseModel):
    name: Optional[str] = None
    fields: Optional[List[DocumentFieldCreate]] = None

class DocumentTemplateRead(DocumentTemplateBase):
    id: int
    company_id: int
    fields: List[DocumentFieldRead] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Document Upload Field Schema (for actual document uploads)
class DocumentUploadFieldRequest(BaseModel):
    field_id: str
    value: str  # Will be handled as string in request, files handled separately

class DocumentUploadRequest(BaseModel):
    employee_id: str
    fields: List[DocumentUploadFieldRequest] = []

class DocumentUploadResponse(BaseModel):
    id: int
    template_id: int
    employee_id: str
    uploaded_at: datetime
    file_paths: dict  # field_id -> file_path mapping

    class Config:
        from_attributes = True