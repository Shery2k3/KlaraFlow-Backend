from pydantic import BaseModel
from typing import List, Optional

class DesignationBase(BaseModel):
    name: str

class DesignationCreate(DesignationBase):
    # Inherits the 'name: str' field, making it required for creation.
    pass

class DesignationUpdate(BaseModel):
    name: Optional[str] = None

class DesignationRead(DesignationBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True

class DesignationList(BaseModel):
    designations: List[DesignationRead]