from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base # Navigate up to the shared base
import enum

class OnboardingStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    EXPIRED = "expired"

class OnboardingSession(Base):
    __tablename__ = 'onboarding_sessions'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    new_employee_email = Column(String, nullable=False, index=True)
    invitation_token = Column(String, nullable=False, unique=True)
    status = Column(Enum(OnboardingStatus), default=OnboardingStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    tasks = relationship("OnboardingTask", back_populates="session", cascade="all, delete-orphan")