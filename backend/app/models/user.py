from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class WearableConnection(BaseModel):
    provider: str  # fitbit, apple_health, samsung_health
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    connected_at: Optional[datetime] = None
    is_active: bool = False


class UserPreferences(BaseModel):
    units: str = "imperial"  # imperial or metric
    default_gym_id: Optional[str] = None
    notifications_enabled: bool = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: str = Field(..., min_length=2, max_length=50)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    preferences: Optional[UserPreferences] = None


class UserInDB(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: str
    password_hash: str
    display_name: str
    saved_gyms: list[str] = []
    wearable_connections: dict[str, WearableConnection] = {}
    preferences: UserPreferences = UserPreferences()
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    saved_gyms: list[str] = []
    wearable_connections: dict[str, WearableConnection] = {}
    preferences: UserPreferences = UserPreferences()
    created_at: datetime
