from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from klaraflow.config.database import get_db
from klaraflow.dependencies.auth import get_current_active_admin
from klaraflow.models import User
from klaraflow.schemas import department_schema
from klaraflow.crud import department_crud
from klaraflow.base.responses import create_response
from klaraflow.base.exceptions import APIException
from klaraflow.config.database import db_manager

router = APIRouter()

@router.post("")
async def create_department(department: department_schema.DepartmentCreate, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        new_dept = await department_crud.create_department(db=db, department=department, company_id=current_admin.company_id)
        return create_response(data=department_schema.DepartmentRead.from_orm(new_dept), message="Department created successfully")

@router.get("")
async def read_departments(current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        depts = await department_crud.get_departments_by_company(db, company_id=current_admin.company_id)
        return create_response(data=[department_schema.DepartmentRead.from_orm(d) for d in depts])

@router.get("/{department_id}")
async def read_department(department_id: int, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        dept = await department_crud.get_department(db, department_id=department_id, company_id=current_admin.company_id)
        if dept is None:
            raise APIException(status_code=404, message="Department not found")
        return create_response(data=department_schema.DepartmentRead.from_orm(dept))

@router.put("/{department_id}")
async def update_department(department_id: int, department_in: department_schema.DepartmentUpdate, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        db_department = await department_crud.get_department(db, department_id=department_id, company_id=current_admin.company_id)
        if db_department is None:
            raise APIException(status_code=404, message="Department not found")
        updated_dept = await department_crud.update_department(db=db, db_department=db_department, department_in=department_in)
        return create_response(data=department_schema.DepartmentRead.from_orm(updated_dept), message="Department updated successfully")

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(department_id: int, current_admin: User = Depends(get_current_active_admin)):
    async with db_manager.session() as db:
        db_department = await department_crud.get_department(db, department_id=department_id, company_id=current_admin.company_id)
        if db_department is None:
            raise APIException(status_code=404, message="Department not found")
        await department_crud.delete_department(db=db, db_department=db_department)