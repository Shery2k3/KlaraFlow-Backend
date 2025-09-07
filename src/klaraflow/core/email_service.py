from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from klaraflow.config.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False
)

fm = FastMail(conf)

async def send_onboarding_invitation(email_to: str, token: str):
    html_content = f"""
    <h2>Welcome to KlaraFlow!</h2>
    <p>Please click the link below to complete your profile and set up your account.</p>
    <a href="http://localhost:3001/onboard?token={token}">Complete Your Profile</a>
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