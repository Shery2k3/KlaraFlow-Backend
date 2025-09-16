from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from ..base import Base

class DocumentSubmission(Base):
    __tablename__ = "document_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False)
    employee_id = Column(String, nullable=False)  # Reference to employee
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Store field values and file paths as JSON
    field_values = Column(JSON, nullable=False)  # {field_id: value}
    file_paths = Column(JSON, nullable=True)     # {field_id: file_path}
    
    # Status tracking
    status = Column(String, default="submitted")  # submitted, approved, rejected
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    template = relationship("DocumentTemplate")
    company = relationship("Company")