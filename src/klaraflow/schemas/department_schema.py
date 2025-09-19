from pydantic import BaseModel
from typing import List, Optional

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    # Inherits name from DepartmentBase
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None

class DepartmentRead(DepartmentBase):
    id: int
    company_id: int

    class Config:
        # Pydantic v2 uses model_config, but from_attributes works for now.
        # This allows creating the Pydantic model from a SQLAlchemy ORM object.
        from_attributes = True

class DepartmentList(BaseModel):
    departments: List[DepartmentRead]