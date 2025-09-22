from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

class OnboardingDocument(Base):
    __tablename__ = 'onboarding_documents'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("onboarding_sessions.id"), nullable=False)
    document_template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False)
    file_url = Column(String, nullable=False)

    session = relationship("OnboardingSession", back_populates="uploaded_documents")
    document_template = relationship("DocumentTemplate")