from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from klaraflow.config.database import get_db
from klaraflow.dependencies.auth import get_current_active_admin
from klaraflow.models import User
from klaraflow.schemas import designation_schema
from klaraflow.crud import designation_crud
from klaraflow.base.responses import create_response
from klaraflow.base.exceptions import APIException

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_designation(
    designation_in: designation_schema.DesignationCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Create a new designation for the admin's company."""
    new_desig = await designation_crud.create_designation(
        db=db, designation_in=designation_in, company_id=current_admin.company_id
    )
    response_data = designation_schema.DesignationRead.model_validate(new_desig)
    return create_response(data=response_data, message="Designation created successfully")

@router.get("", response_model=List[designation_schema.DesignationRead])
async def read_designations(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Retrieve all designations for the admin's company."""
    desigs = await designation_crud.get_designations_by_company(db=db, company_id=current_admin.company_id)
    response_data = [designation_schema.DesignationRead.model_validate(d) for d in desigs]
    return create_response(data=response_data)

@router.get("/{designation_id}", response_model=designation_schema.DesignationRead)
async def read_designation(
    designation_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Retrieve a specific designation by ID."""
    desig = await designation_crud.get_designation(db=db, designation_id=designation_id, company_id=current_admin.company_id)
    if desig is None:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Designation not found")
    return create_response(data=designation_schema.DesignationRead.model_validate(desig))

@router.put("/{designation_id}", response_model=designation_schema.DesignationRead)
async def update_designation(
    designation_id: int,
    designation_in: designation_schema.DesignationUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Update a designation."""
    db_designation = await designation_crud.get_designation(db=db, designation_id=designation_id, company_id=current_admin.company_id)
    if db_designation is None:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Designation not found")

    updated_desig = await designation_crud.update_designation(db=db, db_designation=db_designation, designation_in=designation_in)
    return create_response(data=designation_schema.DesignationRead.model_validate(updated_desig), message="Designation updated successfully")

@router.delete("/{designation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_designation(
    designation_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Delete a designation."""
    db_designation = await designation_crud.get_designation(db=db, designation_id=designation_id, company_id=current_admin.company_id)
    if db_designation is None:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Designation not found")

    await designation_crud.delete_designation(db=db, db_designation=db_designation)
    return None