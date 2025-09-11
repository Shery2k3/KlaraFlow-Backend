from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from klaraflow.crud import onboarding_crud
from klaraflow.schemas import onboarding_schema
from klaraflow.config.database import get_db
from klaraflow.dependencies.auth import get_current_active_admin
from klaraflow.models.user_model import User
from klaraflow.schemas.user_schema import Token

router = APIRouter()

@router.post(
    "/invite", 
    response_model=onboarding_schema.OnboardingSessionRead,
    status_code=status.HTTP_201_CREATED
)
async def invite_employee(
    invite_data: onboarding_schema.OnboardingInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin) 
):
    """
    Admin endpoint to invite a new employee to the platform.
    """
    
    session = await onboarding_crud.invite_new_employee(
        db=db,
        invite_data=invite_data,
        company_id=current_admin.company_id
    )
    return session

@router.get("/session/{token}", response_model=onboarding_schema.OnboardingSessionDataResponse)
async def get_onboarding_session_data(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    session = await onboarding_crud.get_session_by_token(db, token=token)
    return session