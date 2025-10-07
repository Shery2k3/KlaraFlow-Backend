# Timesheet Module

This module provides complete timesheet management functionality for the KlaraFlow HRM system.

## Overview

The timesheet module allows employees to:
- Track their daily work hours
- Submit timesheets for approval
- View their timesheet history

And allows administrators to:
- Review submitted timesheets
- Approve or reject timesheets
- View all employee submissions

## Architecture

The module follows the repository's feature-based architecture:

```
src/klaraflow/timesheet/
├── __init__.py         # Module initialization
├── models.py           # Database models (Timesheet, TimeEntry)
├── schemas.py          # Pydantic schemas for API validation
├── crud.py             # Database operations
└── router.py           # FastAPI endpoints
```

## Database Schema

### Timesheet Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users table |
| start_date | Date | Period start date |
| end_date | Date | Period end date |
| status | String | 'Draft', 'Submitted', 'Approved', or 'Rejected' |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |
| submitted_at | DateTime | Submission timestamp (nullable) |
| reviewed_at | DateTime | Review timestamp (nullable) |

### TimeEntry Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| timesheet_id | Integer | Foreign key to timesheets table |
| date | Date | Entry date |
| start_time | Time | Work start time |
| end_time | Time | Work end time |
| notes | Text | Optional notes (nullable) |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

## API Endpoints

### Employee Endpoints

#### GET `/api/v1/timesheet/my-timesheet`
Get the current user's timesheet for a specific period.

**Query Parameters:**
- `start_date` (optional): Period start date (defaults to current week Monday)
- `end_date` (optional): Period end date (defaults to current week Sunday)

**Response:** TimesheetRead schema with all entries

---

#### POST `/api/v1/timesheet/my-timesheet/entries`
Add a new time entry to the current user's timesheet.

**Query Parameters:**
- `start_date` (optional): Period start date
- `end_date` (optional): Period end date

**Request Body:** TimeEntryCreate schema
```json
{
  "date": "2025-01-10",
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "notes": "Working on project X"
}
```

**Response:** TimeEntryRead schema

---

#### PUT `/api/v1/timesheet/my-timesheet/entries/{entry_id}`
Update an existing time entry.

**Path Parameters:**
- `entry_id`: ID of the entry to update

**Query Parameters:**
- `start_date` (optional): Period start date
- `end_date` (optional): Period end date

**Request Body:** TimeEntryUpdate schema (all fields optional)
```json
{
  "notes": "Updated notes"
}
```

**Response:** TimeEntryRead schema

---

#### DELETE `/api/v1/timesheet/my-timesheet/entries/{entry_id}`
Delete a time entry.

**Path Parameters:**
- `entry_id`: ID of the entry to delete

**Query Parameters:**
- `start_date` (optional): Period start date
- `end_date` (optional): Period end date

**Response:** 204 No Content

---

#### POST `/api/v1/timesheet/my-timesheet/submit`
Submit the current timesheet for approval.

**Query Parameters:**
- `start_date` (optional): Period start date
- `end_date` (optional): Period end date

**Response:** TimesheetRead schema with status 'Submitted'

---

### Admin Endpoints

#### GET `/api/v1/timesheet/admin/submissions`
Get all submitted timesheets for review (admin/hr only).

**Response:** Array of TimesheetRead schemas

---

#### PUT `/api/v1/timesheet/admin/submissions/{timesheet_id}/approve`
Approve a submitted timesheet (admin/hr only).

**Path Parameters:**
- `timesheet_id`: ID of the timesheet to approve

**Response:** TimesheetRead schema with status 'Approved'

---

#### PUT `/api/v1/timesheet/admin/submissions/{timesheet_id}/reject`
Reject a submitted timesheet (admin/hr only).

**Path Parameters:**
- `timesheet_id`: ID of the timesheet to reject

**Request Body:** TimesheetReject schema
```json
{
  "reason": "Hours do not match project logs"
}
```

**Response:** TimesheetRead schema with status 'Rejected'

## Business Rules

1. **Timesheet Status Workflow:**
   - Draft → Submitted → Approved/Rejected
   - Only Draft timesheets can be edited
   - Only Submitted timesheets can be approved/rejected

2. **Period Management:**
   - Timesheets are organized by periods (start_date to end_date)
   - By default, the system uses weekly periods (Monday to Sunday)
   - Entries must fall within the timesheet period

3. **Multi-tenancy:**
   - Users can only view/edit their own timesheets
   - Admins can only review timesheets from their company

4. **Auto-creation:**
   - Timesheets are automatically created when an employee adds their first entry for a period

## Installation

1. Run the database migration:
```bash
alembic upgrade head
```

2. Restart the application:
```bash
poetry run poe dev
```

3. The timesheet endpoints will be available at `/api/v1/timesheet/*`

## Testing

Run the validation tests:
```bash
poetry run python tests/test_timesheet_module.py
```

## Future Enhancements

Potential improvements for future iterations:
- Add total hours calculation
- Support for different period types (bi-weekly, monthly)
- Export timesheet to PDF/Excel
- Integration with project/task management
- Overtime and leave tracking
- Bulk approval for admins
- Email notifications on submission/approval
- Timesheet templates
- Holiday and weekend handling
