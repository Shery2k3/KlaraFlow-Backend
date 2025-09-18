from fastapi import Request, APIRouter, Depends, status, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from klaraflow.crud import onboarding_crud
from klaraflow.schemas import onboarding_schema
from klaraflow.config.database import get_db
from klaraflow.dependencies.auth import get_current_active_admin
from klaraflow.models.user_model import User
from klaraflow.schemas.user_schema import Token
from klaraflow.base.responses import create_response
from klaraflow.base.exceptions import APIException
from klaraflow.core.s3_service import s3_service
import logging

logger = logging.getLogger("klaraflow.onboarding")
logging.basicConfig(
    level=logging.INFO,  # Or DEBUG for more details
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

router = APIRouter()

@router.post(
    "/invite", 
    response_model=onboarding_schema.OnboardingSessionRead
)
async def invite_employee(
    # invite_data: onboarding_schema.OnboardingInviteRequest,
    request: Request,
    profilePic: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin) 
):
    """
    Admin endpoint to invite a new employee to the platform.
    Handles multipart/form-data for optional profile picture upload.
    """
    
    # Testing
    form = await request.form()
    invite_data = onboarding_schema.OnboardingInviteRequest(
        empId=form.get("empId"),
        firstName=form.get("firstName"),
        lastName=form.get("lastName"),
        email=form.get("email"),
        gender=form.get("gender"),
        userRole=form.get("userRole"),
        phone=form.get("phone"),
        designation=form.get("designation"),
        department=form.get("department"),
        jobType=form.get("jobType"),
        hiringDate=form.get("hiringDate"),
        template_id=form.get("template_id"),
        reportTo=form.get("reportTo"),
        grade=form.get("grade"),
        probationPeriod=form.get("probationPeriod"),
        dateOfBirth=form.get("dateOfBirth"),
        maritalStatus=form.get("maritalStatus"),
        nationality=form.get("nationality"),
    )
    #Over
    
    profile_picture_url = None
    if profilePic:
        folder = f"profile_pictures/{current_admin.company_id}"
        logger.info(f"Uploading file to S3: {profilePic.filename} -> {folder}")
        profile_picture_url = await s3_service.upload_file(profilePic, folder)
        logger.info(f"File uploaded. S3 URL: {profile_picture_url}")
    else:
        logger.info("No avatar_file provided in request.")

    session = await onboarding_crud.invite_new_employee(
        db=db,
        invite_data=invite_data,
        company_id=current_admin.company_id,
        profile_picture_url=profile_picture_url
    )
    logger.info(f"Session created. profile_picture_url in DB: {getattr(session, 'profile_picture_url', None)}")
    session_response = onboarding_schema.OnboardingSessionRead.model_validate(session)
    
    return create_response(
        data=session_response.model_dump(mode="json"),
        message="Invitation sent successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.get("/session/{token}", response_model=onboarding_schema.OnboardingSessionDataResponse)
async def get_onboarding_session_data(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    session = await onboarding_crud.get_session_by_token(db, token=token)
    return create_response(
        data=session,
        message="Session data retrieved successfully",
        status_code=status.HTTP_200_OK
    )   