from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class GymType(str, Enum):
    GYM = "gym"
    BASKETBALL_COURT = "basketball_court"
    BOTH = "both"


class BusyLevel(int, Enum):
    EMPTY = 1
    LIGHT = 2
    MODERATE = 3
    BUSY = 4
    PACKED = 5


BUSY_LEVEL_LABELS = {
    1: "Empty",
    2: "Light",
    3: "Moderate",
    4: "Busy",
    5: "Packed",
}


class Location(BaseModel):
    type: str = "Point"
    coordinates: list[float] = [0.0, 0.0]  # [longitude, latitude]


class GymCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    gym_type: GymType = GymType.GYM
    amenities: list[str] = []
    description: Optional[str] = None


class GymUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    gym_type: Optional[GymType] = None
    amenities: Optional[list[str]] = None
    description: Optional[str] = None


class GymResponse(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    location: Optional[Location] = None
    gym_type: GymType
    amenities: list[str] = []
    description: Optional[str] = None
    created_by: str
    current_busy_level: Optional[float] = None
    busy_level_label: Optional[str] = None
    recent_reports_count: int = 0
    created_at: datetime


class CrowdReportCreate(BaseModel):
    gym_id: str
    busy_level: BusyLevel
    notes: Optional[str] = None


class CrowdReportResponse(BaseModel):
    id: str
    gym_id: str
    user_id: str
    user_display_name: str
    busy_level: int
    busy_level_label: str
    notes: Optional[str] = None
    timestamp: datetime


class BasketballReportCreate(BaseModel):
    gym_id: str
    player_count: int = Field(..., ge=0, le=100)
    notes: Optional[str] = None


class BasketballReportResponse(BaseModel):
    id: str
    gym_id: str
    user_id: str
    user_display_name: str
    player_count: int
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    timestamp: datetime


# --- Popular Times models ---

class HourlyBusyness(BaseModel):
    hour: int  # 0-23
    level: float  # average busyness 1-5


class PopularTimesDay(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    day_name: str
    hours: list[HourlyBusyness]


class PopularTimesResponse(BaseModel):
    gym_id: str
    gym_name: str
    days: list[PopularTimesDay]
    current_hour_level: Optional[float] = None
    current_day: Optional[str] = None
    current_hour: Optional[int] = None
