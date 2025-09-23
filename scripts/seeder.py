import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from klaraflow.config.settings import settings
from klaraflow.core.security import get_hash_password
from klaraflow.models import Base, Company, User

#? --- Run ---
# poetry run python -m scripts.seeder

# --- Configuration ---
# This is the data for your first company and its admin
COMPANY_NAME = "KlaraFlow"
ADMIN_EMAIL = "admin@klaraflow.io"
ADMIN_PASSWORD = "klaraflow"  # Change this!


async def seed_database():
    """
    Connects to the database, creates all tables if they don't exist,
    and seeds the initial company and admin user.
    """
    print("--- Starting Database Seeding ---")

    # Create an engine and session factory for this standalone script
    engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=False)
    AsyncSessionFactory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create all tables defined by our models
    async with engine.begin() as conn:
        # Dropping all tables for a clean seed (optional, for development)
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created (if they didn't exist).")

    async with AsyncSessionFactory() as session:
        # Check if the company already exists
        company_result = await session.execute(
            Company.__table__.select().where(Company.name == COMPANY_NAME)
        )
        if company_result.first():
            print(f"⚠️ Company '{COMPANY_NAME}' already exists. Skipping.")
            return

        # --- Create the Company and Admin ---
        print(f"🌱 Seeding company: {COMPANY_NAME}")
        db_company = Company(name=COMPANY_NAME)
        session.add(db_company)
        await session.flush()  # Flush to get the company ID

        print(f"👤 Seeding admin user: {ADMIN_EMAIL}")
        hashed_password = get_hash_password(ADMIN_PASSWORD)
        db_admin = User(
            email=ADMIN_EMAIL,
            hashed_password=hashed_password,
            company_id=db_company.id,
            role="admin",
            is_active=True,
        )
        session.add(db_admin)

        await session.commit()
        print("✅ Seeding complete!")

    await engine.dispose()
    print("--- Database Seeding Finished ---")


if __name__ == "__main__":
    asyncio.run(seed_database())
