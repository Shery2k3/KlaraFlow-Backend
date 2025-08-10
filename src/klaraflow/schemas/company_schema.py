from pydantic import BaseModel, EmailStr

# Schema for creating a new company and its first admin
class CompanyCreate(BaseModel):
  company_name: str
  admin_email: EmailStr
  admin_password: str

# Public schema to return  
class CompanyPublic(BaseModel):
  id: int
  name: str
  
  class Config:
    from_attributes = True