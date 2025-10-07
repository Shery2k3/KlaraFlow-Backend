from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date, timedelta

from klaraflow.config.database import get_db
from klaraflow.dependencies.auth import get_current_active_user, get_current_active_admin
from klaraflow.models.user_model import User
from klaraflow.timesheet import schemas, crud
from klaraflow.base.responses import create_response
from klaraflow.base.exceptions import APIException

router = APIRouter()


def get_current_week() -> tuple[date, date]:
    """Get start and end date of the current week (Monday to Sunday)"""
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday
    return start_of_week, end_of_week


@router.get("/my-timesheet", response_model=schemas.TimesheetRead)
async def get_my_timesheet(
    start_date: date = Query(None, description="Start date of the period (defaults to current week Monday)"),
    end_date: date = Query(None, description="End date of the period (defaults to current week Sunday)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the current user's timesheet for a specific period"""
    # Use current week if dates not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_current_week()
    
    # Get or create timesheet for the period
    timesheet = await crud.get_or_create_timesheet_for_period(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return create_response(
        data=schemas.TimesheetRead.model_validate(timesheet),
        message="Timesheet retrieved successfully"
    )


@router.post("/my-timesheet/entries", status_code=status.HTTP_201_CREATED)
async def add_time_entry(
    entry_in: schemas.TimeEntryCreate,
    start_date: date = Query(None, description="Start date of the period"),
    end_date: date = Query(None, description="End date of the period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a new time entry to the current user's timesheet"""
    # Use current week if dates not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_current_week()
    
    # Get or create timesheet
    timesheet = await crud.get_or_create_timesheet_for_period(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Check if timesheet is in Draft status
    if timesheet.status != schemas.TimesheetStatus.DRAFT.value:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Cannot add entries to a timesheet with status: {timesheet.status}"
        )
    
    # Validate that entry date is within timesheet period
    if not (timesheet.start_date <= entry_in.date <= timesheet.end_date):
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Entry date must be within the timesheet period"
        )
    
    # Create the entry
    entry = await crud.create_time_entry(
        db=db,
        timesheet_id=timesheet.id,
        entry=entry_in
    )
    
    return create_response(
        data=schemas.TimeEntryRead.model_validate(entry),
        message="Time entry created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.put("/my-timesheet/entries/{entry_id}")
async def update_time_entry(
    entry_id: int,
    entry_in: schemas.TimeEntryUpdate,
    start_date: date = Query(None, description="Start date of the period"),
    end_date: date = Query(None, description="End date of the period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a time entry"""
    # Use current week if dates not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_current_week()
    
    # Get user's timesheet
    timesheet = await crud.get_user_timesheet(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    if not timesheet:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Timesheet not found"
        )
    
    # Check if timesheet is in Draft status
    if timesheet.status != schemas.TimesheetStatus.DRAFT.value:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Cannot update entries in a timesheet with status: {timesheet.status}"
        )
    
    # Get the entry
    db_entry = await crud.get_time_entry(
        db=db,
        entry_id=entry_id,
        timesheet_id=timesheet.id
    )
    
    if not db_entry:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Time entry not found"
        )
    
    # Validate that updated date (if provided) is within timesheet period
    if entry_in.date and not (timesheet.start_date <= entry_in.date <= timesheet.end_date):
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Entry date must be within the timesheet period"
        )
    
    # Update the entry
    updated_entry = await crud.update_time_entry(
        db=db,
        db_entry=db_entry,
        entry_in=entry_in
    )
    
    return create_response(
        data=schemas.TimeEntryRead.model_validate(updated_entry),
        message="Time entry updated successfully"
    )


@router.delete("/my-timesheet/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_entry(
    entry_id: int,
    start_date: date = Query(None, description="Start date of the period"),
    end_date: date = Query(None, description="End date of the period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a time entry"""
    # Use current week if dates not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_current_week()
    
    # Get user's timesheet
    timesheet = await crud.get_user_timesheet(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    if not timesheet:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Timesheet not found"
        )
    
    # Check if timesheet is in Draft status
    if timesheet.status != schemas.TimesheetStatus.DRAFT.value:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Cannot delete entries from a timesheet with status: {timesheet.status}"
        )
    
    # Get the entry
    db_entry = await crud.get_time_entry(
        db=db,
        entry_id=entry_id,
        timesheet_id=timesheet.id
    )
    
    if not db_entry:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Time entry not found"
        )
    
    # Delete the entry
    await crud.delete_time_entry(db=db, db_entry=db_entry)
    
    return None


@router.post("/my-timesheet/submit")
async def submit_timesheet(
    start_date: date = Query(None, description="Start date of the period"),
    end_date: date = Query(None, description="End date of the period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit the current timesheet for approval"""
    # Use current week if dates not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_current_week()
    
    # Get user's timesheet
    timesheet = await crud.get_user_timesheet(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    if not timesheet:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Timesheet not found"
        )
    
    # Check if timesheet is in Draft status
    if timesheet.status != schemas.TimesheetStatus.DRAFT.value:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Cannot submit a timesheet with status: {timesheet.status}"
        )
    
    # Submit the timesheet
    submitted_timesheet = await crud.submit_timesheet(db=db, timesheet=timesheet)
    
    return create_response(
        data=schemas.TimesheetRead.model_validate(submitted_timesheet),
        message="Timesheet submitted successfully"
    )


@router.get("/admin/submissions", response_model=List[schemas.TimesheetRead])
async def get_submitted_timesheets(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Get all submitted timesheets for admin review"""
    timesheets = await crud.get_submitted_timesheets(
        db=db,
        company_id=current_admin.company_id
    )
    
    response_data = [schemas.TimesheetRead.model_validate(ts) for ts in timesheets]
    return create_response(data=response_data)


@router.put("/admin/submissions/{timesheet_id}/approve")
async def approve_timesheet(
    timesheet_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Approve a submitted timesheet"""
    # Get the timesheet
    timesheet = await crud.get_timesheet_by_id(db=db, timesheet_id=timesheet_id)
    
    if not timesheet:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Timesheet not found"
        )
    
    # Check that the timesheet belongs to the admin's company
    if timesheet.user.company_id != current_admin.company_id:
        raise APIException(
            status_code=status.HTTP_403_FORBIDDEN,
            message="You don't have permission to approve this timesheet"
        )
    
    # Check if timesheet is in Submitted status
    if timesheet.status != schemas.TimesheetStatus.SUBMITTED.value:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Cannot approve a timesheet with status: {timesheet.status}"
        )
    
    # Approve the timesheet
    approved_timesheet = await crud.approve_timesheet(db=db, timesheet=timesheet)
    
    return create_response(
        data=schemas.TimesheetRead.model_validate(approved_timesheet),
        message="Timesheet approved successfully"
    )


@router.put("/admin/submissions/{timesheet_id}/reject")
async def reject_timesheet(
    timesheet_id: int,
    rejection_data: schemas.TimesheetReject,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Reject a submitted timesheet"""
    # Get the timesheet
    timesheet = await crud.get_timesheet_by_id(db=db, timesheet_id=timesheet_id)
    
    if not timesheet:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Timesheet not found"
        )
    
    # Check that the timesheet belongs to the admin's company
    if timesheet.user.company_id != current_admin.company_id:
        raise APIException(
            status_code=status.HTTP_403_FORBIDDEN,
            message="You don't have permission to reject this timesheet"
        )
    
    # Check if timesheet is in Submitted status
    if timesheet.status != schemas.TimesheetStatus.SUBMITTED.value:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Cannot reject a timesheet with status: {timesheet.status}"
        )
    
    # Reject the timesheet
    rejected_timesheet = await crud.reject_timesheet(db=db, timesheet=timesheet)
    
    return create_response(
        data=schemas.TimesheetRead.model_validate(rejected_timesheet),
        message="Timesheet rejected successfully"
    )
