from pydantic import BaseModel
from typing import List

class DesignationBase(BaseModel):
    name: str

class DesignationCreate(DesignationBase):
    pass

class DesignationUpdate(DesignationBase):
    pass

class DesignationRead(DesignationBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True

class DesignationList(BaseModel):
    designations: List[DesignationRead]