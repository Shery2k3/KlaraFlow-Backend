from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from klaraflow.models.user_model import User
from klaraflow.models.onboarding.session_model import OnboardingSession
from klaraflow.schemas.user_schema import UserCreate
from klaraflow.core.security import get_hash_password, verify_password
from klaraflow.models.department_model import Department
from klaraflow.models.designation_model import Designation
from klaraflow.base.exceptions import APIException
from fastapi import status

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Retrieve a user by their email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
  
async def create_user_from_onboarding(db: AsyncSession, *, session: OnboardingSession, hashed_password: str) -> User:
    # Validate referenced Department and Designation IDs if provided
    designation_id = getattr(session, "designation_id", None)
    department_id = getattr(session, "department_id", None)

    if designation_id is not None:
        result = await db.execute(select(Designation).where(Designation.id == designation_id))
        des = result.scalar_one_or_none()
        if des is None:
            raise APIException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Designation id={designation_id} not found")

    if department_id is not None:
        result = await db.execute(select(Department).where(Department.id == department_id))
        dept = result.scalar_one_or_none()
        if dept is None:
            raise APIException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Department id={department_id} not found")

    db_user = User(
        company_id=session.company_id,
        profile_picture_url=getattr(session, "profile_picture_url", None),
        email=session.new_employee_email,
        hashed_password=hashed_password,
        first_name=session.firstName,
        last_name=session.lastName,
        is_active=True,
        role=session.userRole or "employee",

        # --- Transfer ALL other details ---
        empId=session.empId,
        phone=session.phone,
        gender=session.gender,
        designation_id=designation_id,
        department_id=department_id,
        jobType=session.jobType,
        hiringDate=session.hiringDate,
        reportTo=session.reportTo,
        grade=session.grade,
        probationPeriod=session.probationPeriod,
        dateOfBirth=session.dateOfBirth,
        maritalStatus=session.maritalStatus,
        nationality=session.nationality
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
