from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base
from .company_model import Company

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # --- Multi-tenancy Key ---
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # --- Basic Info ---
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True) # Will be filled during onboarding
    last_name = Column(String, nullable=True)
    
    # --- Status & Roles ---
    is_active = Column(Boolean, default=False) # Should be False until onboarding is complete
    role = Column(String, nullable=False, default="employee") # e.g., 'employee', 'admin', 'hr'
    
    # --- Timestamps ---
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # --- Relationships ---
    company = relationship("Company", back_populates="users")

    # --- Employee Details (Can be in a separate Profile model later) ---
    phone = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    department = Column(String, nullable=True)