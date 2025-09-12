from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from klaraflow.models.onboarding.session_model import OnboardingSession
from klaraflow.schemas.onboarding_schema import OnboardingInviteRequest, OnboardingActivationRequest
from klaraflow.core.security import create_access_token, get_hash_password
from klaraflow.core.email_service import send_onboarding_invitation
from klaraflow.crud import user_crud
from klaraflow.core.responses import create_response
from klaraflow.core.exceptions import APIException

async def invite_new_employee(db: AsyncSession, *, invite_data: OnboardingInviteRequest, company_id: int):
    #? Check for existing pending invites
    existing_session = select(OnboardingSession).where(
        OnboardingSession.new_employee_email == invite_data.email,
        OnboardingSession.status == "pending"
    )
    result = await db.execute(existing_session)
    if result.scalar_one_or_none():
        raise APIException(status_code=status.HTTP_409_CONFLICT, message="An active invitation for this email already exists.", errors=["Duplicate invitation."])
    
    expires_delta = timedelta(hours=24)
    expires_at = datetime.now(timezone.utc) + expires_delta
    
    token_data = {
        "sub": invite_data.email, 
        "cid": company_id,
        "scope": "onboarding_invitation"
    }
    invitation_token = create_access_token(data=token_data, expires_delta=expires_delta)

    # We'll create the user with a placeholder, inactive status.
    # The actual user record will be fully created after onboarding.
    # For now, we store the essential info in the session.
    db_session = OnboardingSession(
        company_id=company_id,
        new_employee_email=invite_data.email,
        invitation_token=invitation_token,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
        empId=invite_data.empId,
        firstName=invite_data.firstName,
        lastName=invite_data.lastName,
        phone=invite_data.phone,
        gender=invite_data.gender,
        userRole=invite_data.userRole,
        designation=invite_data.designation,
        department=invite_data.department,
        jobType=invite_data.jobType,
        hiringDate=invite_data.hiringDate,
        reportTo=invite_data.reportTo,
        grade=invite_data.grade,
        probationPeriod=invite_data.probationPeriod,
        dateOfBirth=invite_data.dateOfBirth,
        maritalStatus=invite_data.maritalStatus,
        nationality=invite_data.nationality
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    
    await send_onboarding_invitation(
        email_to=invite_data.email, 
        token=invitation_token
    )
    
    return db_session

async def get_session_by_token(db: AsyncSession, token: str) -> OnboardingSession:
    statement = select(OnboardingSession).where(OnboardingSession.invitation_token == token)
    result = await db.execute(statement)
    session = result.scalar_one_or_none()
    
    if not session:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Invitation link is invalid or has been used.", errors=["Invalid or used token."])
    
    if session.status != "pending":
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST, message="This invitation has already been used or is no longer valid.", errors=["Invitation not pending."])

    if session.expires_at < datetime.now(timezone.utc):
        session.status = "expired"
        await db.commit()
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST, message="This invitation link has expired.", errors=["Token expired."])
        
    return session

async def activate_employee_account(db: AsyncSession, *, activation_data: OnboardingActivationRequest):
    # 1. Get and validate the session using our new function
    session = await get_session_by_token(db, token=activation_data.token)
    
    # 2. Hash the new password provided by the employee
    hashed_password = get_hash_password(activation_data.password)
    
    # 3. Create the permanent user record in the 'users' table
    new_user = await user_crud.create_user_from_onboarding(
        db,
        session=session,
        hashed_password=hashed_password
    )
    
    # 4. Mark the temporary onboarding session as 'completed'
    session.status = "completed"
    await db.commit()
    
    # 5. Create a login token for the new user so they are immediately logged in
    login_token = create_access_token(data={"sub": new_user.email})
    
    return {"access_token": login_token, "token_type": "bearer"}