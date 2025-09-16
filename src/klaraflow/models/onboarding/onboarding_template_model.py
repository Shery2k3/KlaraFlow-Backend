from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from ..base import Base

# Association tables for many-to-many relationships
onboarding_template_required_documents = Table(
    'onboarding_template_required_documents',
    Base.metadata,
    Column('onboarding_template_id', Integer, ForeignKey('onboarding_templates.id'), primary_key=True),
    Column('document_template_id', Integer, ForeignKey('document_templates.id'), primary_key=True)
)

onboarding_template_optional_documents = Table(
    'onboarding_template_optional_documents', 
    Base.metadata,
    Column('onboarding_template_id', Integer, ForeignKey('onboarding_templates.id'), primary_key=True),
    Column('document_template_id', Integer, ForeignKey('document_templates.id'), primary_key=True)
)

class OnboardingTemplate(Base):
    __tablename__ = "onboarding_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="onboarding_templates")
    todos = relationship("TodoItem", back_populates="template", cascade="all, delete-orphan")
    
    # Document relationships
    required_documents = relationship("DocumentTemplate", 
                                    secondary=onboarding_template_required_documents,
                                    back_populates="required_in_onboarding")
    optional_documents = relationship("DocumentTemplate", 
                                    secondary=onboarding_template_optional_documents,
                                    back_populates="optional_in_onboarding")
    
    # Sessions using this template
    sessions = relationship("OnboardingSession", back_populates="template")