from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str
    SECRET_KEY: str
    DEBUG: bool = False
    ENVIRONMENT: str
    
    class Config:
        env_file = ".env.development"

settings = Settings()