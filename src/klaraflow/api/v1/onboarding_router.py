from fastapi import Request, APIRouter, Depends, status, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from klaraflow.crud import onboarding_crud
from klaraflow.schemas import onboarding_schema
from klaraflow.config.database import get_db
from klaraflow.dependencies.auth import get_current_active_admin, get_current_active_user
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
    # TODO: Fix the pydantic model parsing with multipart/form-data
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
        onboardingTemplateId=form.get("onboardingTemplateId")
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
    
@router.get("/session/status/{token}", response_model=onboarding_schema.OnboardingStatusResponse)
async def get_onboarding_session_status(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    session = await onboarding_crud.get_session_by_token(db, token=token)
    return create_response(
        data={"status": session.status, "current_step": session.current_step},
        message="Session status retrieved successfully",
        status_code=status.HTTP_200_OK
    )

@router.put("/session/step/{token}", response_model=onboarding_schema.OnboardingSessionRead)
async def update_onboarding_step(
    token: str,
    step_data: onboarding_schema.OnboardingStepUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    session = await onboarding_crud.update_onboarding_step(db, token=token, step_data=step_data)
    return create_response(
        data=session,
        message="Onboarding step updated successfully",
        status_code=status.HTTP_200_OK
    )

@router.get("/my-data", response_model=onboarding_schema.OnboardingDataRead)
async def get_my_onboarding_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    data = await onboarding_crud.get_onboarding_data_for_user(db, user_email=current_user.email)
    return create_response(
        data=data,
        message="Onboarding data retrieved successfully",
        status_code=status.HTTP_200_OK
    )

@router.put("/step", response_model=onboarding_schema.OnboardingDataRead)
async def update_my_onboarding_step(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    session = await onboarding_crud.get_onboarding_session_for_user(db, user_email=current_user.email)
    session.current_step += 1
    await db.commit()
    await db.refresh(session)
    
    # Return updated data
    data = await onboarding_crud.get_onboarding_data_for_user(db, user_email=current_user.email)
    return create_response(
        data=data,
        message="Onboarding step updated successfully",
        status_code=status.HTTP_200_OK
    )

@router.put("/todos/{todo_id}")
async def update_todo(
    todo_id: int,
    completed: bool, # Send completion status in the request body
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    await onboarding_crud.update_todo_for_user(db, user_email=current_user.email, todo_id=todo_id, completed=completed)
    return create_response(
        data=None,
        message="Todo updated successfully",
        status_code=status.HTTP_200_OK
    )

@router.post("/submit")
async def submit_onboarding(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    await onboarding_crud.submit_onboarding(db, user_email=current_user.email)
    return create_response(
        data=None,
        message="Onboarding completed successfully",
        status_code=status.HTTP_200_OK
    )

@router.put("/my-data")
async def update_my_onboarding_data(
    employee_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    session = await onboarding_crud.get_onboarding_session_for_user(db, user_email=current_user.email)
    
    # Update session fields
    for key, value in employee_data.items():
        if hasattr(session, key):
            setattr(session, key, value)
    
    await db.commit()
    await db.refresh(session)
    
    # Return updated data
    data = await onboarding_crud.get_onboarding_data_for_user(db, user_email=current_user.email)
    return create_response(
        data=data,
        message="Onboarding data updated successfully",
        status_code=status.HTTP_200_OK
    )


@router.put("/review", response_model=onboarding_schema.OnboardingDataRead)
async def review_and_update_my_info(
    request: Request,
    profilePic: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Endpoint for the user to review their pre-filled information (provided by HR) and edit
    allowed fields. Accepts multipart/form-data so profile picture can be uploaded.
    """
    form = await request.form()

    # Collect allowed fields from the multipart form
    update_data = {
        "firstName": form.get("firstName"),
        "lastName": form.get("lastName"),
        "email": form.get("email"),
        "phone": form.get("phone"),
        "gender": form.get("gender"),
        "dateOfBirth": form.get("dateOfBirth"),
        "maritalStatus": form.get("maritalStatus"),
        "nationality": form.get("nationality"),
    }

    # Call CRUD to update the session and optionally upload profile picture
    updated_data = await onboarding_crud.update_onboarding_review_for_user(
        db=db,
        user_email=current_user.email,
        update_data=update_data,
        profile_file=profilePic
    )
    
    # Increment to step 2 (Document Upload) after review
    await onboarding_crud.increment_step_for_user(db, user_email=current_user.email)

    return create_response(
        data=updated_data,
        message="Onboarding info updated successfully",
        status_code=status.HTTP_200_OK
    )

@router.post("/documents/upload")
async def upload_onboarding_document(
    document_template_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    session = await onboarding_crud.get_onboarding_session_for_user(db, user_email=current_user.email)
    
    # Upload to S3
    folder = f"onboarding_documents/{current_user.company_id}/{session.id}"
    file_url = await s3_service.upload_file(file, folder)
    
    # Save document record in DB
    await onboarding_crud.save_uploaded_document(
        db,
        user_email=current_user.email,
        document_template_id=document_template_id,
        file_url=file_url
    )
    
    return create_response(
        data={"file_url": file_url},
        message="Document uploaded successfully",
        status_code=status.HTTP_201_CREATED
    )
