from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from ..base import Base
import enum

class FieldTypeEnum(str, enum.Enum):
    TEXT = "text"
    TEXTAREA = "textarea"  
    FILE = "file"
    DATE = "date"

class FieldWidthEnum(str, enum.Enum):
    HALF = "half"
    FULL = "full"

class DocumentTemplate(Base):
    __tablename__ = "document_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="document_templates")
    fields = relationship("DocumentField", back_populates="template", cascade="all, delete-orphan")
    
    # For onboarding templates
    required_in_onboarding = relationship("OnboardingTemplate", 
                                        secondary="onboarding_template_required_documents", 
                                        back_populates="required_documents")
    optional_in_onboarding = relationship("OnboardingTemplate", 
                                        secondary="onboarding_template_optional_documents", 
                                        back_populates="optional_documents")

class DocumentField(Base):
    __tablename__ = "document_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False)
    
    label = Column(String, nullable=False)
    field_type = Column(Enum(FieldTypeEnum), nullable=False)
    placeholder = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    required = Column(Boolean, default=False, nullable=False)
    width = Column(Enum(FieldWidthEnum), default=FieldWidthEnum.FULL, nullable=False)
    
    # Field order for consistent display
    order_index = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    template = relationship("DocumentTemplate", back_populates="fields")