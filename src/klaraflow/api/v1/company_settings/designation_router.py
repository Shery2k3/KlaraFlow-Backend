from fastapi import APIRouter, Depends, status
from typing import List

from klaraflow.config.database import db_manager
from klaraflow.dependencies.auth import get_current_active_admin
from klaraflow.models import User
from klaraflow.schemas import designation_schema
from klaraflow.crud import designation_crud
from klaraflow.base.responses import create_response
from klaraflow.base.exceptions import APIException

router = APIRouter()

@router.post("")
async def create_designation(designation: designation_schema.DesignationCreate, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        new_desig = await designation_crud.create_designation(db=db, designation=designation, company_id=current_admin.company_id)
        return create_response(data=designation_schema.DesignationRead.from_orm(new_desig), message="Designation created successfully")

@router.get("")
async def read_designations(current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        desigs = await designation_crud.get_designations_by_company(db, company_id=current_admin.company_id)
        return create_response(data=[designation_schema.DesignationRead.from_orm(d) for d in desigs])

@router.get("/{designation_id}")
async def read_designation(designation_id: int, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        desig = await designation_crud.get_designation(db, designation_id=designation_id, company_id=current_admin.company_id)
        if desig is None:
            raise APIException(status_code=404, message="Designation not found")
        return create_response(data=designation_schema.DesignationRead.from_orm(desig))

@router.put("/{designation_id}")
async def update_designation(designation_id: int, designation_in: designation_schema.DesignationUpdate, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        db_designation = await designation_crud.get_designation(db, designation_id=designation_id, company_id=current_admin.company_id)
        if db_designation is None:
            raise APIException(status_code=404, message="Designation not found")
        updated_desig = await designation_crud.update_designation(db=db, db_designation=db_designation, designation_in=designation_in)
        return create_response(data=designation_schema.DesignationRead.from_orm(updated_desig), message="Designation updated successfully")

@router.delete("/{designation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_designation(designation_id: int, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        db_designation = await designation_crud.get_designation(db, designation_id=designation_id, company_id=current_admin.company_id)
        if db_designation is None:
            raise APIException(status_code=404, message="Designation not found")
        await designation_crud.delete_designation(db=db, db_designation=db_designation)