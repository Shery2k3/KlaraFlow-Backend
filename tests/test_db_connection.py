import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

async def test_connection():
    # Test async connection
    DATABASE_URL = "postgresql+asyncpg://klaraflow_user:klaraflow@localhost:5432/klaraflow"
    
    engine = create_async_engine(DATABASE_URL)
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            print("✅ Connection successful!")
            print(f"PostgreSQL version: {result.fetchone()[0]}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        await engine.dispose()

# Run test
asyncio.run(test_connection())

# Terminal: `python /tests/test_db_connection.py`