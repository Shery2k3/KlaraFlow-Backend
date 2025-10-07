from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time, Date, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from klaraflow.models.base import Base


class Timesheet(Base):
    __tablename__ = "timesheets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Period definition
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status: 'Draft', 'Submitted', 'Approved', 'Rejected'
    status = Column(String, nullable=False, default="Draft")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="timesheets")
    entries = relationship("TimeEntry", back_populates="timesheet", cascade="all, delete-orphan")


class TimeEntry(Base):
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    timesheet_id = Column(Integer, ForeignKey("timesheets.id"), nullable=False)
    
    # Entry details
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    timesheet = relationship("Timesheet", back_populates="entries")
