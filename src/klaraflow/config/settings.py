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

    class Config:
        env_file = ".env.development"

settings = Settings()