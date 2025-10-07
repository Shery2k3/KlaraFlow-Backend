from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date, timedelta
from klaraflow.timesheet.models import Timesheet, TimeEntry
from klaraflow.timesheet.schemas import (
    TimeEntryCreate, 
    TimeEntryUpdate, 
    TimesheetStatus
)


# TimeEntry CRUD
async def create_time_entry(
    db: AsyncSession, 
    timesheet_id: int, 
    entry: TimeEntryCreate
) -> TimeEntry:
    """Create a new time entry for a timesheet"""
    db_entry = TimeEntry(**entry.model_dump(), timesheet_id=timesheet_id)
    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry


async def get_time_entry(
    db: AsyncSession, 
    entry_id: int, 
    timesheet_id: int
) -> Optional[TimeEntry]:
    """Get a specific time entry by ID"""
    statement = select(TimeEntry).where(
        TimeEntry.id == entry_id,
        TimeEntry.timesheet_id == timesheet_id
    )
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def update_time_entry(
    db: AsyncSession, 
    db_entry: TimeEntry, 
    entry_in: TimeEntryUpdate
) -> TimeEntry:
    """Update a time entry"""
    update_data = entry_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_entry, field, value)
    
    await db.commit()
    await db.refresh(db_entry)
    return db_entry


async def delete_time_entry(db: AsyncSession, db_entry: TimeEntry):
    """Delete a time entry"""
    await db.delete(db_entry)
    await db.commit()


# Timesheet CRUD
async def get_or_create_timesheet_for_period(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date
) -> Timesheet:
    """Get existing timesheet or create a new one for a period"""
    statement = select(Timesheet).where(
        Timesheet.user_id == user_id,
        Timesheet.start_date == start_date,
        Timesheet.end_date == end_date
    ).options(selectinload(Timesheet.entries))
    
    result = await db.execute(statement)
    timesheet = result.scalar_one_or_none()
    
    if not timesheet:
        timesheet = Timesheet(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            status=TimesheetStatus.DRAFT.value
        )
        db.add(timesheet)
        await db.commit()
        await db.refresh(timesheet, attribute_names=['entries'])
    
    return timesheet


async def get_user_timesheet(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date
) -> Optional[Timesheet]:
    """Get a user's timesheet for a specific period"""
    statement = select(Timesheet).where(
        Timesheet.user_id == user_id,
        Timesheet.start_date == start_date,
        Timesheet.end_date == end_date
    ).options(selectinload(Timesheet.entries))
    
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def get_timesheet_by_id(
    db: AsyncSession,
    timesheet_id: int,
    user_id: Optional[int] = None
) -> Optional[Timesheet]:
    """Get a timesheet by ID, optionally filtered by user"""
    statement = select(Timesheet).where(Timesheet.id == timesheet_id)
    
    if user_id is not None:
        statement = statement.where(Timesheet.user_id == user_id)
    
    statement = statement.options(selectinload(Timesheet.entries))
    
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def submit_timesheet(db: AsyncSession, timesheet: Timesheet) -> Timesheet:
    """Submit a timesheet for approval"""
    timesheet.status = TimesheetStatus.SUBMITTED.value
    timesheet.submitted_at = datetime.now()
    await db.commit()
    await db.refresh(timesheet)
    return timesheet


async def get_submitted_timesheets(
    db: AsyncSession,
    company_id: int
) -> List[Timesheet]:
    """Get all submitted timesheets for admin review (filtered by company)"""
    statement = (
        select(Timesheet)
        .join(Timesheet.user)
        .where(
            Timesheet.status == TimesheetStatus.SUBMITTED.value
        )
        .options(selectinload(Timesheet.entries))
        .order_by(Timesheet.submitted_at.desc())
    )
    
    result = await db.execute(statement)
    timesheets = result.scalars().all()
    
    # Filter by company_id
    return [ts for ts in timesheets if ts.user.company_id == company_id]


async def approve_timesheet(db: AsyncSession, timesheet: Timesheet) -> Timesheet:
    """Approve a timesheet"""
    timesheet.status = TimesheetStatus.APPROVED.value
    timesheet.reviewed_at = datetime.now()
    await db.commit()
    await db.refresh(timesheet)
    return timesheet


async def reject_timesheet(db: AsyncSession, timesheet: Timesheet) -> Timesheet:
    """Reject a timesheet"""
    timesheet.status = TimesheetStatus.REJECTED.value
    timesheet.reviewed_at = datetime.now()
    await db.commit()
    await db.refresh(timesheet)
    return timesheet
