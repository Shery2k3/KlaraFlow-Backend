from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
  __tablename__ = "users"
  
  id = Column(Integer, primary_key=True, index=True)
  company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
  email = Column(String, unique=True, index=True, nullable=False)
  hashed_password = Column(String, nullable=False)
  is_active = Column(Boolean, default=True)
  role = Column(String, nullable=False, default="employee")
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  
  company = relationship("Company", back_populates="users")
