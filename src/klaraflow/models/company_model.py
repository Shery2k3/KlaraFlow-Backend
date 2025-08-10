from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Company(Base):
  __tablename__ = 'companies'
  
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False, index=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  
  users = relationship("User", back_populates='company')