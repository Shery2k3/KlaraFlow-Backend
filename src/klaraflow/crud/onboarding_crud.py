from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from klaraflow.models.onboarding.session_model import OnboardingSession
from klaraflow.schemas.onboarding_schema import OnboardingInviteRequest
from klaraflow.core.security import create_access_token
from klaraflow.core.email_service import send_onboarding_invitation

async def invite_new_employee(db: AsyncSession, *, invite_data: OnboardingInviteRequest, company_id: int):
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
        # You might add columns to OnboardingSession to store this pre-filled data
        # for the employee to review. For now, we'll just pass the email.
        invitation_token=invitation_token,
        expires_at=expires_at
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    
    await send_onboarding_invitation(
        email_to=invite_data.email, 
        token=invitation_token
    )
    
    return db_session