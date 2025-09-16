from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from klaraflow.crud import onboarding_template_crud
from klaraflow.schemas import onboarding_schema
from klaraflow.config.database import get_db
from klaraflow.dependencies.auth import get_current_active_admin
from klaraflow.models.user_model import User
from klaraflow.base.responses import create_response
from klaraflow.base.exceptions import APIException

router = APIRouter()

@router.post(
    "/templates",
    response_model=onboarding_schema.OnboardingTemplateRead,
    status_code=status.HTTP_201_CREATED
)
async def create_onboarding_template(
    template_data: onboarding_schema.OnboardingTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Create a new onboarding template"""
    
    template = await onboarding_template_crud.create_onboarding_template(
        db=db,
        template_data=template_data,
        company_id=current_admin.company_id
    )
    
    # Convert SQLAlchemy model to Pydantic schema
    template_response = onboarding_schema.OnboardingTemplateRead.model_validate(template)
    
    return create_response(
        data=template_response.model_dump(mode='json'),
        message="Onboarding template created successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.get(
    "/templates",
    response_model=List[onboarding_schema.OnboardingTemplateRead]
)
async def get_onboarding_templates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Get all onboarding templates for the company"""
    
    templates = await onboarding_template_crud.get_onboarding_templates(
        db=db,
        company_id=current_admin.company_id,
        skip=skip,
        limit=limit
    )
    
    # Convert SQLAlchemy models to Pydantic schemas
    templates_response = [onboarding_schema.OnboardingTemplateRead.model_validate(template) for template in templates]
    
    return create_response(
        data=[template.model_dump(mode='json') for template in templates_response],
        message="Onboarding templates retrieved successfully",
        status_code=status.HTTP_200_OK
    )

@router.get(
    "/templates/{template_id}",
    response_model=onboarding_schema.OnboardingTemplateRead
)
async def get_onboarding_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Get a specific onboarding template"""
    
    template = await onboarding_template_crud.get_onboarding_template_by_id(
        db=db,
        template_id=template_id,
        company_id=current_admin.company_id
    )
    
    if not template:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Onboarding template not found"
        )
    
    # Convert SQLAlchemy model to Pydantic schema
    template_response = onboarding_schema.OnboardingTemplateRead.model_validate(template)
    
    return create_response(
        data=template_response.model_dump(mode='json'),
        message="Onboarding template retrieved successfully",
        status_code=status.HTTP_200_OK
    )

@router.put(
    "/templates/{template_id}",
    response_model=onboarding_schema.OnboardingTemplateRead
)
async def update_onboarding_template(
    template_id: int,
    template_data: onboarding_schema.OnboardingTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Update an onboarding template"""
    
    template = await onboarding_template_crud.update_onboarding_template(
        db=db,
        template_id=template_id,
        template_data=template_data,
        company_id=current_admin.company_id
    )
    
    # Convert SQLAlchemy model to Pydantic schema
    template_response = onboarding_schema.OnboardingTemplateRead.model_validate(template)
    
    return create_response(
        data=template_response.model_dump(mode='json'),
        message="Onboarding template updated successfully",
        status_code=status.HTTP_200_OK
    )

@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_onboarding_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Delete an onboarding template"""
    
    await onboarding_template_crud.delete_onboarding_template(
        db=db,
        template_id=template_id,
        company_id=current_admin.company_id
    )
    
    return create_response(
        data=None,
        message="Onboarding template deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT
    )