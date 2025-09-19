from pydantic import BaseModel
from typing import List

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    pass

class DepartmentRead(DepartmentBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True

class DepartmentList(BaseModel):
    departments: List[DepartmentRead]