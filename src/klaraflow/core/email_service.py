from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from klaraflow.config.settings import settings
from pydantic import EmailStr
from typing import List

# --- Configuration ---
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=EmailStr(settings.MAIL_FROM),
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)

async def send_onboarding_invitation(email_to: EmailStr, token: str):
    """
    Sends the onboarding invitation email to a new employee.
    """
    html_content = f"""
    <h2>Welcome to KlaraFlow!</h2>
    <p>Please click the link below to complete your profile and set up your account.</p>
    <a href="http://localhost:3000/invite/{token}">Complete Your Profile</a>
    <p>This link will expire in 24 hours.</p>
    """
    
    message = MessageSchema(
        subject="Your KlaraFlow Onboarding Invitation",
        recipients=[email_to],
        body=html_content,
        subtype="html"
    )
    
    await fm.send_message(message)
    print(f"Onboarding email sent to {email_to}")