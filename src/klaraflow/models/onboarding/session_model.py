from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

class OnboardingSession(Base):
    __tablename__ = "onboarding_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    new_employee_email = Column(String, nullable=False, index=True)
    status = Column(String, default="pending")
    
    invitation_token = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    empId = Column(String, nullable=True)
    firstName = Column(String, nullable=True)
    lastName = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    userRole = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    department = Column(String, nullable=True)
    jobType = Column(String, nullable=True)
    hiringDate = Column(String, nullable=True)
    reportTo = Column(String, nullable=True)
    grade = Column(String, nullable=True)
    probationPeriod = Column(String, nullable=True)
    dateOfBirth = Column(String, nullable=True)
    maritalStatus = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    
    tasks = relationship("OnboardingTask", back_populates="session")