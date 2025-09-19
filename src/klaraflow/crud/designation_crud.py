from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from klaraflow.models import Designation, User
from klaraflow.schemas import designation_schema

async def get_designation(db: AsyncSession, *, designation_id: int, company_id: int) -> Optional[Designation]:
    """Get a single designation by ID, ensuring it belongs to the correct company."""
    statement = select(Designation).where(Designation.id == designation_id, Designation.company_id == company_id)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_designations_by_company(db: AsyncSession, *, company_id: int) -> List[Designation]:
    """Get all designations for a specific company, ordered by name."""
    statement = select(Designation).where(Designation.company_id == company_id).order_by(Designation.name)
    result = await db.execute(statement)
    return result.scalars().all()

async def create_designation(db: AsyncSession, *, designation_in: designation_schema.DesignationCreate, company_id: int) -> Designation:
    """Create a new designation for a company."""
    # model_dump() is the Pydantic v2 equivalent of .dict()
    db_designation = Designation(**designation_in.model_dump(), company_id=company_id)
    db.add(db_designation)
    await db.commit()
    await db.refresh(db_designation)
    return db_designation

async def update_designation(
    db: AsyncSession,
    *,
    db_designation: Designation,
    designation_in: designation_schema.DesignationUpdate
) -> Designation:
    """Update an existing designation."""
    # model_dump(exclude_unset=True) ensures we only update fields that were actually sent
    update_data = designation_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_designation, field, value)
    await db.commit()
    await db.refresh(db_designation)
    return db_designation

async def delete_designation(db: AsyncSession, *, db_designation: Designation):
    """Delete a designation."""
    # Consider checking if any employees are assigned to this designation before deleting
    await db.delete(db_designation)
    await db.commit()
    return {"ok": True}