from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Designation(Base):
    __tablename__ = "designations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    company = relationship("Company")
    employees = relationship("User", back_populates="designation")