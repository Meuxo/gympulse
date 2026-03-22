from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
import os
import uuid
from app.database import get_db
from app.auth.jwt import get_current_user
from app.models.gym import BasketballReportCreate, BasketballReportResponse
from app.utils.helpers import serialize_doc, serialize_docs
from app.config import get_settings

router = APIRouter(prefix="/basketball", tags=["Basketball"])

settings = get_settings()


@router.post("/reports", status_code=201)
async def submit_basketball_report(
    gym_id: str,
    player_count: int,
    notes: Optional[str] = None,
    photo: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    gym = await db.gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        raise HTTPException(status_code=404, detail="Gym/court not found")

    photo_url = None
    if photo:
        # Validate file type
        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Check file size
        contents = await photo.read()
        if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB")

        # Save file
        ext = photo.filename.split(".")[-1] if "." in photo.filename else "jpg"
        filename = f"basketball_{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(contents)
        photo_url = f"/uploads/{filename}"

    report_doc = {
        "gym_id": gym_id,
        "user_id": current_user["_id"],
        "user_display_name": current_user["display_name"],
        "player_count": player_count,
        "photo_url": photo_url,
        "notes": notes,
        "timestamp": datetime.utcnow(),
    }
    result = await db.basketball_reports.insert_one(report_doc)
    report_doc["_id"] = result.inserted_id
    return serialize_doc(report_doc)


@router.get("/reports/{gym_id}")
async def get_basketball_reports(
    gym_id: str,
    hours: int = Query(4, ge=1, le=24),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_db()
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    cursor = db.basketball_reports.find({
        "gym_id": gym_id,
        "timestamp": {"$gte": cutoff},
    }).sort("timestamp", -1).limit(limit)

    reports = await cursor.to_list(length=limit)
    return {"reports": serialize_docs(reports), "count": len(reports)}


@router.get("/courts")
async def list_basketball_courts(
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """List gyms/courts that have basketball facilities."""
    db = get_db()
    query = {"gym_type": {"$in": ["basketball_court", "both"]}}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}

    cursor = db.gyms.find(query).sort("name", 1).skip(skip).limit(limit)
    courts = await cursor.to_list(length=limit)

    # Enrich with latest basketball report info
    enriched = []
    for court in courts:
        doc = serialize_doc(court)
        cutoff = datetime.utcnow() - timedelta(hours=4)
        recent = await db.basketball_reports.find({
            "gym_id": doc["id"],
            "timestamp": {"$gte": cutoff},
        }).sort("timestamp", -1).to_list(10)

        if recent:
            avg_players = sum(r["player_count"] for r in recent) / len(recent)
            doc["avg_player_count"] = round(avg_players, 1)
            doc["latest_report"] = serialize_doc(recent[0])
            doc["recent_reports_count"] = len(recent)
        else:
            doc["avg_player_count"] = None
            doc["latest_report"] = None
            doc["recent_reports_count"] = 0

        enriched.append(doc)

    total = await db.gyms.count_documents(query)
    return {"courts": enriched, "total": total}
