from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from klaraflow.crud import user_crud, department_crud, designation_crud
from klaraflow.models import User

async def assign_department(db: AsyncSession, employee_id: int, department_id: int, company_id: int) -> User:
    employee = await user_crud.get_user(db, user_id=employee_id)
    if not employee or employee.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    department = await department_crud.get_department(db, department_id=department_id, company_id=company_id)
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        
    employee.department_id = department_id
    await db.commit()
    await db.refresh(employee)
    return employee

async def remove_department(db: AsyncSession, employee_id: int, company_id: int) -> User:
    employee = await user_crud.get_user(db, user_id=employee_id)
    if not employee or employee.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        
    employee.department_id = None
    await db.commit()
    await db.refresh(employee)
    return employee

async def assign_designation(db: AsyncSession, employee_id: int, designation_id: int, company_id: int) -> User:
    employee = await user_crud.get_user(db, user_id=employee_id)
    if not employee or employee.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    designation = await designation_crud.get_designation(db, designation_id=designation_id, company_id=company_id)
    if not designation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Designation not found")
        
    employee.designation_id = designation_id
    await db.commit()
    await db.refresh(employee)
    return employee

async def remove_designation(db: AsyncSession, employee_id: int, company_id: int) -> User:
    employee = await user_crud.get_user(db, user_id=employee_id)
    if not employee or employee.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        
    employee.designation_id = None
    await db.commit()
    await db.refresh(employee)
    return employee