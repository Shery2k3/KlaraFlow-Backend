from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from klaraflow.models.user_model import User
from klaraflow.models.onboarding.session_model import OnboardingSession
from klaraflow.schemas.user_schema import UserCreate
from klaraflow.core.security import get_hash_password, verify_password

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Retrieve a user by their email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
  
async def create_user_from_onboarding(db: AsyncSession, *, session: OnboardingSession, hashed_password: str) -> User:
    db_user = User(
        company_id=session.company_id,
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
        designation=session.designation,
        department=session.department,
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
