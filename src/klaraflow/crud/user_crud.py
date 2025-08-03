from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from klaraflow.models.user_model import User
from klaraflow.schemas.user_schema import UserCreate
from klaraflow.core.security import get_hash_password, verify_password

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Retrieve a user by their email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
  
async def create_user(db: AsyncSession, user: UserCreate):
  """Create a user"""
  hashed_password = get_hash_password(user.password)
  db_user = User(email=user.email, hashed_password=hashed_password)
  db.add(db_user)
  await db.commit()
  await db.refresh(db_user)
  return db_user