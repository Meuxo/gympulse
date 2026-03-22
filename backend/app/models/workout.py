from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MuscleGroup(str, Enum):
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    LEGS = "legs"
    GLUTES = "glutes"
    CORE = "core"
    FULL_BODY = "full_body"
    CARDIO = "cardio"
    OTHER = "other"


class WorkoutType(str, Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    HIIT = "hiit"
    YOGA = "yoga"
    SPORTS = "sports"
    FLEXIBILITY = "flexibility"
    OTHER = "other"


class Exercise(BaseModel):
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None  # in lbs or kg based on user preference
    distance: Optional[float] = None  # in miles or km
    duration: Optional[int] = None  # in seconds
    calories: Optional[float] = None
    notes: Optional[str] = None


class WorkoutCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    workout_type: WorkoutType = WorkoutType.STRENGTH
    muscle_groups: list[MuscleGroup] = []
    exercises: list[Exercise] = []
    date: datetime = Field(default_factory=datetime.utcnow)
    total_duration: Optional[int] = None  # in minutes
    total_calories: Optional[float] = None
    notes: Optional[str] = None


class WorkoutUpdate(BaseModel):
    title: Optional[str] = None
    workout_type: Optional[WorkoutType] = None
    muscle_groups: Optional[list[MuscleGroup]] = None
    exercises: Optional[list[Exercise]] = None
    date: Optional[datetime] = None
    total_duration: Optional[int] = None
    total_calories: Optional[float] = None
    notes: Optional[str] = None


class WorkoutResponse(BaseModel):
    id: str
    user_id: str
    title: str
    workout_type: WorkoutType
    muscle_groups: list[MuscleGroup]
    exercises: list[Exercise]
    date: datetime
    total_duration: Optional[int] = None
    total_calories: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
