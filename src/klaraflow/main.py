from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from klaraflow.config.database import db_manager, get_db
from klaraflow.api.v1 import auth_router, onboarding_router
from klaraflow.api.v1.settings import document_router, onboarding_template_router
from klaraflow.base.exceptions import api_exception_handler, validation_exception_handler, APIException

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    await db_manager.connect()
    yield
    # On shutdown
    await db_manager.disconnect()

app = FastAPI(
    title="KlaraFlow HRM",
    description="Multi-tenant HRM SaaS platform",
    lifespan=lifespan,
)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Welcome route
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
    
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(onboarding_router.router, prefix="/api/v1/onboarding", tags=["Employee Onboarding"])
app.include_router(document_router.router, prefix="/api/v1/document", tags=["Document Templates"])
app.include_router(onboarding_template_router.router, prefix="/api/v1/onboarding-template", tags=["Onboarding Templates"])

# poetry run uvicorn src.main:app --reload --port 3000
# poetry run poe dev