from pydantic import BaseModel, EmailStr
from datetime import datetime

# Data shape for creating a user
class UserCreate(BaseModel):
  email: EmailStr
  password: str
  
# Data shape for returning a user to public
class UserPublic(BaseModel):
  id: int
  email: EmailStr
  is_active: bool
  created_at: datetime
  
  class Config:
    from_attributes = True

# Properties for the login response token
class Token(BaseModel):
  access_token: str
  token_type: str