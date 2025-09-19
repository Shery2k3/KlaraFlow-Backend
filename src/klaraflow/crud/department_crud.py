from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from klaraflow.models import Department
from klaraflow.schemas import department_schema
from typing import List

async def get_department(db: AsyncSession, department_id: int, company_id: int) -> Department | None:
    statement = select(Department).where(Department.id == department_id, Department.company_id == company_id)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_departments_by_company(db: AsyncSession, company_id: int) -> List[Department]:
    statement = select(Department).where(Department.company_id == company_id).order_by(Department.name)
    result = await db.execute(statement)
    return result.scalars().all()

async def create_department(db: AsyncSession, department: department_schema.DepartmentCreate, company_id: int) -> Department:
    db_department = Department(**department.model_dump(), company_id=company_id)
    db.add(db_department)
    await db.commit()
    await db.refresh(db_department)
    return db_department

async def update_department(db: AsyncSession, db_department: Department, department_in: department_schema.DepartmentUpdate) -> Department:
    db_department.name = department_in.name
    await db.commit()
    await db.refresh(db_department)
    return db_department

async def delete_department(db: AsyncSession, db_department: Department):
    await db.delete(db_department)
    await db.commit()