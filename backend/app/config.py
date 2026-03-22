from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "GymPulse"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "gympulse"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production-use-a-real-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Wearable API keys
    FITBIT_CLIENT_ID: str = ""
    FITBIT_CLIENT_SECRET: str = ""
    FITBIT_REDIRECT_URI: str = "http://localhost:8000/api/wearables/fitbit/callback"

    APPLE_HEALTH_KEY: str = ""

    SAMSUNG_HEALTH_CLIENT_ID: str = ""
    SAMSUNG_HEALTH_CLIENT_SECRET: str = ""

    # Google Places API
    GOOGLE_PLACES_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Frontend URL (for OAuth redirects)
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
