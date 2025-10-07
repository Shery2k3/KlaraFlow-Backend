from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date, time
from enum import Enum


class TimesheetStatus(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"


# TimeEntry Schemas
class TimeEntryBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    notes: Optional[str] = None


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    notes: Optional[str] = None


class TimeEntryRead(TimeEntryBase):
    id: int
    timesheet_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Timesheet Schemas
class TimesheetBase(BaseModel):
    start_date: date
    end_date: date
    status: TimesheetStatus


class TimesheetRead(TimesheetBase):
    id: int
    user_id: int
    entries: List[TimeEntryRead] = []
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TimesheetSubmit(BaseModel):
    """Schema for submitting a timesheet"""
    pass


class TimesheetApprove(BaseModel):
    """Schema for approving a timesheet"""
    pass


class TimesheetReject(BaseModel):
    """Schema for rejecting a timesheet"""
    reason: Optional[str] = None
