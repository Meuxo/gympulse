from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class WearableProvider(str, Enum):
    FITBIT = "fitbit"
    APPLE_HEALTH = "apple_health"
    SAMSUNG_HEALTH = "samsung_health"


class MetricType(str, Enum):
    STEPS = "steps"
    HEART_RATE = "heart_rate"
    CALORIES_BURNED = "calories_burned"
    SLEEP_DURATION = "sleep_duration"
    SLEEP_QUALITY = "sleep_quality"
    ACTIVE_MINUTES = "active_minutes"
    DISTANCE = "distance"
    FLOORS_CLIMBED = "floors_climbed"
    WORKOUT_SESSION = "workout_session"


class WearableSyncCreate(BaseModel):
    provider: WearableProvider
    metric_type: MetricType
    value: float
    unit: str  # e.g., "steps", "bpm", "kcal", "minutes", "miles"
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Optional[dict[str, Any]] = None


class WearableSyncResponse(BaseModel):
    id: str
    user_id: str
    provider: WearableProvider
    metric_type: MetricType
    value: float
    unit: str
    recorded_at: datetime
    synced_at: datetime
    raw_data: Optional[dict[str, Any]] = None


class WearableSyncBatch(BaseModel):
    """For bulk importing data from a wearable device."""
    provider: WearableProvider
    data: list[WearableSyncCreate]


class WearableDailySummary(BaseModel):
    date: str
    steps: Optional[float] = None
    heart_rate_avg: Optional[float] = None
    calories_burned: Optional[float] = None
    sleep_duration: Optional[float] = None
    active_minutes: Optional[float] = None
    distance: Optional[float] = None
