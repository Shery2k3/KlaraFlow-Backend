from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from klaraflow.models import Designation
from klaraflow.schemas import designation_schema
from typing import List

async def get_designation(db: AsyncSession, designation_id: int, company_id: int) -> Designation | None:
    statement = select(Designation).where(Designation.id == designation_id, Designation.company_id == company_id)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_designations_by_company(db: AsyncSession, company_id: int) -> List[Designation]:
    statement = select(Designation).where(Designation.company_id == company_id).order_by(Designation.name)
    result = await db.execute(statement)
    return result.scalars().all()

async def create_designation(db: AsyncSession, designation: designation_schema.DesignationCreate, company_id: int) -> Designation:
    db_designation = Designation(**designation.model_dump(), company_id=company_id)
    db.add(db_designation)
    await db.commit()
    await db.refresh(db_designation)
    return db_designation

async def update_designation(db: AsyncSession, db_designation: Designation, designation_in: designation_schema.DesignationUpdate) -> Designation:
    db_designation.name = designation_in.name
    await db.commit()
    await db.refresh(db_designation)
    return db_designation

async def delete_designation(db: AsyncSession, db_designation: Designation):
    await db.delete(db_designation)
    await db.commit()