from pydantic import BaseModel, EmailStr
from .company_schema import CompanyPublic
from datetime import datetime

# Data shape for creating a user
class UserCreate(BaseModel):
    email: EmailStr
    password: str
  
# Data shape for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str
  
# Data shape for returning a user to public
class UserPublic(BaseModel):
    id: int
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    role: str
    empId: str | None
    phone: str | None
    gender: str | None
    department: str | None = None
    designation: str | None = None

    class Config:
        from_attributes = True

# Properties for the login response token
class Token(BaseModel):
    access_token: str
    token_type: str