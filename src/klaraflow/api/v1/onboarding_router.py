from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from klaraflow.crud import onboarding_crud
from klaraflow.schemas import onboarding_schema
from klaraflow.config.database import get_db
# This will be replaced by a real authentication dependency
from .auth_router import get_current_active_user 

router = APIRouter()

@router.post(
    "/invite", 
    response_model=onboarding_schema.OnboardingSessionRead,
    status_code=status.HTTP_201_CREATED
)
async def invite_employee(
    invite_data: onboarding_schema.OnboardingInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_active_user) 
):
    """
    Admin endpoint to invite a new employee to the platform.
    """
    # In a real app, you would add a check here to ensure current_admin.role == 'admin'
    
    session = await onboarding_crud.invite_new_employee(
        db=db,
        invite_data=invite_data,
        company_id=current_admin.company_id
    )
    return session