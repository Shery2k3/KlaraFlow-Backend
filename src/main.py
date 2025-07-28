from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import db_manager, get_db
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - like your Express connectDB()
    await db_manager.connect()
    yield
    # Shutdown - clean up connections
    await db_manager.disconnect()

app = FastAPI(
    title="KlaraFlow HRM",
    description="Multi-tenant HRM SaaS platform",
    lifespan=lifespan,
)

# This is like your Express route
@app.get("/")
async def read_root():
    return {"message": "KlaraFlow HRM API", "status": "running"}

# Test database connection endpoint
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check if database is accessible"""
    try:
        from sqlalchemy import text
        result = await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": db_manager.db_name,
            "connection": "active"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
    
# poetry run uvicorn src.main:app --reload --port 3000