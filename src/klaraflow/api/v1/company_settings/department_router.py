from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from klaraflow.config.database import get_db
from klaraflow.dependencies.auth import get_current_active_admin
from klaraflow.models import User
from klaraflow.schemas import department_schema
from klaraflow.crud import department_crud
from klaraflow.base.responses import create_response
from klaraflow.base.exceptions import APIException

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_department(
    department_in: department_schema.DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Create a new department for the admin's company."""
    new_dept = await department_crud.create_department(
        db=db, department_in=department_in, company_id=current_admin.company_id
    )
    # Use model_validate (from_orm is deprecated in Pydantic v2)
    response_data = department_schema.DepartmentRead.model_validate(new_dept)
    return create_response(data=response_data, message="Department created successfully")

@router.get("", response_model=List[department_schema.DepartmentRead])
async def read_departments(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Retrieve all departments for the admin's company."""
    depts = await department_crud.get_departments_by_company(db=db, company_id=current_admin.company_id)
    response_data = [department_schema.DepartmentRead.model_validate(d) for d in depts]
    return create_response(data=response_data)

@router.get("/{department_id}", response_model=department_schema.DepartmentRead)
async def read_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Retrieve a specific department by ID."""
    dept = await department_crud.get_department(db=db, department_id=department_id, company_id=current_admin.company_id)
    if dept is None:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Department not found")
    return create_response(data=department_schema.DepartmentRead.model_validate(dept))

@router.put("/{department_id}", response_model=department_schema.DepartmentRead)
async def update_department(
    department_id: int,
    department_in: department_schema.DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Update a department."""
    db_department = await department_crud.get_department(db=db, department_id=department_id, company_id=current_admin.company_id)
    if db_department is None:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Department not found")
    
    updated_dept = await department_crud.update_department(db=db, db_department=db_department, department_in=department_in)
    return create_response(data=department_schema.DepartmentRead.model_validate(updated_dept), message="Department updated successfully")

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Delete a department."""
    db_department = await department_crud.get_department(db=db, department_id=department_id, company_id=current_admin.company_id)
    if db_department is None:
        # We can return 204 even if it doesn't exist, as the end state is the same.
        # Or raise a 404 if the frontend needs to know. Let's be explicit.
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Department not found")
    
    await department_crud.delete_department(db=db, db_department=db_department)
    # For 204, it's best to return no body.
    return None