from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from typing import Optional
from bson import ObjectId
from app.database import get_db
from app.auth.jwt import get_current_user
from app.models.workout import (
    WorkoutCreate, WorkoutUpdate, WorkoutResponse,
    WorkoutType, MuscleGroup,
)
from app.utils.helpers import serialize_doc, serialize_docs

router = APIRouter(prefix="/workouts", tags=["Workouts"])


@router.post("/", status_code=201)
async def create_workout(workout: WorkoutCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    workout_doc = {
        "user_id": current_user["_id"],
        "title": workout.title,
        "workout_type": workout.workout_type.value,
        "muscle_groups": [mg.value for mg in workout.muscle_groups],
        "exercises": [ex.model_dump() for ex in workout.exercises],
        "date": workout.date,
        "total_duration": workout.total_duration,
        "total_calories": workout.total_calories,
        "notes": workout.notes,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.workouts.insert_one(workout_doc)
    workout_doc["_id"] = result.inserted_id
    return serialize_doc(workout_doc)


@router.get("/")
async def list_workouts(
    current_user: dict = Depends(get_current_user),
    workout_type: Optional[WorkoutType] = None,
    muscle_group: Optional[MuscleGroup] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_db()
    query = {"user_id": current_user["_id"]}

    if workout_type:
        query["workout_type"] = workout_type.value
    if muscle_group:
        query["muscle_groups"] = muscle_group.value
    if date_from or date_to:
        query["date"] = {}
        if date_from:
            query["date"]["$gte"] = date_from
        if date_to:
            query["date"]["$lte"] = date_to

    cursor = db.workouts.find(query).sort("date", -1).skip(skip).limit(limit)
    workouts = await cursor.to_list(length=limit)
    total = await db.workouts.count_documents(query)

    return {
        "workouts": serialize_docs(workouts),
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{workout_id}")
async def get_workout(workout_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    workout = await db.workouts.find_one({
        "_id": ObjectId(workout_id),
        "user_id": current_user["_id"],
    })
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return serialize_doc(workout)


@router.put("/{workout_id}")
async def update_workout(
    workout_id: str,
    update_data: WorkoutUpdate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    update_fields = {}
    for field, value in update_data.model_dump(exclude_none=True).items():
        if field == "muscle_groups" and value is not None:
            update_fields[field] = [mg.value if hasattr(mg, "value") else mg for mg in value]
        elif field == "exercises" and value is not None:
            update_fields[field] = [ex if isinstance(ex, dict) else ex.model_dump() for ex in value]
        elif field == "workout_type" and value is not None:
            update_fields[field] = value.value if hasattr(value, "value") else value
        else:
            update_fields[field] = value

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_fields["updated_at"] = datetime.utcnow()
    result = await db.workouts.update_one(
        {"_id": ObjectId(workout_id), "user_id": current_user["_id"]},
        {"$set": update_fields},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"message": "Workout updated"}


@router.delete("/{workout_id}")
async def delete_workout(workout_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.workouts.delete_one({
        "_id": ObjectId(workout_id),
        "user_id": current_user["_id"],
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"message": "Workout deleted"}


@router.get("/stats/summary")
async def workout_stats(current_user: dict = Depends(get_current_user)):
    """Get workout statistics for the current user."""
    db = get_db()
    pipeline = [
        {"$match": {"user_id": current_user["_id"]}},
        {"$group": {
            "_id": None,
            "total_workouts": {"$sum": 1},
            "total_duration": {"$sum": {"$ifNull": ["$total_duration", 0]}},
            "total_calories": {"$sum": {"$ifNull": ["$total_calories", 0]}},
            "workout_types": {"$addToSet": "$workout_type"},
        }},
    ]
    results = await db.workouts.aggregate(pipeline).to_list(1)
    if not results:
        return {
            "total_workouts": 0,
            "total_duration": 0,
            "total_calories": 0,
            "workout_types": [],
        }
    stats = results[0]
    del stats["_id"]
    return stats
