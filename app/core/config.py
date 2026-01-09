from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FIREBASE_SERVICE_ACCOUNT: str
    FIREBASE_WEB_API_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

settings = Settings()
