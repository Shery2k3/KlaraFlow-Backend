# In BE/src/klaraflow/config/settings.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str
    SECRET_KEY: str
    DEBUG: bool = False
    ENVIRONMENT: str
    JWT_ALG: str

    # Email service
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    # S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str
    AWS_REGION: str

    class Config:
        env_file = ".env.development"

settings = Settings()