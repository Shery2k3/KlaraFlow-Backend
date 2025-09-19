from fastapi import APIRouter, Depends, status
from klaraflow.config.database import db_manager
from klaraflow.dependencies.auth import get_current_active_admin
from klaraflow.models import User
from klaraflow.schemas import user_schema
from klaraflow.services import employee_service
from klaraflow.base.responses import create_response

router = APIRouter()

@router.put("/{employee_id}/department/{department_id}")
async def assign_department_to_employee(employee_id: int, department_id: int, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        employee = await employee_service.assign_department(db, employee_id, department_id, current_admin.company_id)
        return create_response(data=user_schema.UserPublic.from_orm(employee), message="Department assigned successfully")

@router.delete("/{employee_id}/department")
async def remove_department_from_employee(employee_id: int, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        employee = await employee_service.remove_department(db, employee_id, current_admin.company_id)
        return create_response(data=user_schema.UserPublic.from_orm(employee), message="Department removed successfully")

@router.put("/{employee_id}/designation/{designation_id}")
async def assign_designation_to_employee(employee_id: int, designation_id: int, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        employee = await employee_service.assign_designation(db, employee_id, designation_id, current_admin.company_id)
        return create_response(data=user_schema.UserPublic.from_orm(employee), message="Designation assigned successfully")

@router.delete("/{employee_id}/designation")
async def remove_designation_from_employee(employee_id: int, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        employee = await employee_service.remove_designation(db, employee_id, current_admin.company_id)
        return create_response(data=user_schema.UserPublic.from_orm(employee), message="Designation removed successfully")