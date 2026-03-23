from fastapi import APIRouter, HTTPException, Depends, Query, Body
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
from app.database import get_db
from app.auth.jwt import get_current_user
from app.models.gym import (
    GymCreate, GymUpdate, GymResponse,
    CrowdReportCreate, CrowdReportResponse,
    BusyLevel, BUSY_LEVEL_LABELS,
    PopularTimesResponse, PopularTimesDay, HourlyBusyness,
)
from app.utils.helpers import serialize_doc, serialize_docs, weighted_average_busy_level
from app.services.google_places import (
    search_place, get_place_busyness, fetch_google_popular_times, link_gym_to_google,
)

router = APIRouter(prefix="/gyms", tags=["Gyms"])

REPORT_WINDOW_HOURS = 2
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


async def _enrich_gym(gym_doc: dict) -> dict:
    """Add current busy level info to a gym document. Falls back to Google data."""
    db = get_db()
    gym = serialize_doc(gym_doc)
    cutoff = datetime.utcnow() - timedelta(hours=REPORT_WINDOW_HOURS)
    reports = await db.crowd_reports.find({
        "gym_id": str(gym_doc.get("_id", gym_doc.get("id"))),
        "timestamp": {"$gte": cutoff},
    }).to_list(50)

    busy_level = weighted_average_busy_level(reports)
    gym["current_busy_level"] = busy_level
    gym["data_source"] = "user_reports" if busy_level is not None else None

    if busy_level is not None:
        rounded = round(busy_level)
        gym["busy_level_label"] = BUSY_LEVEL_LABELS.get(rounded, "Unknown")
    else:
        # Fallback: check if gym has a Google place_id and try Google
        place_id = gym_doc.get("google_place_id")
        if place_id:
            google_data = await get_place_busyness(place_id)
            if google_data and google_data.get("is_open") is not None:
                # Estimate busyness: if open → 3 (moderate), if closed → 0
                estimated = 3 if google_data["is_open"] else 0
                gym["current_busy_level"] = estimated
                gym["busy_level_label"] = BUSY_LEVEL_LABELS.get(estimated, "Unknown") if estimated > 0 else "Closed"
                gym["data_source"] = "google"
            else:
                gym["busy_level_label"] = None
        else:
            gym["busy_level_label"] = None

    gym["recent_reports_count"] = len(reports)
    gym["google_place_id"] = gym_doc.get("google_place_id")
    gym["google_rating"] = gym_doc.get("google_rating")
    gym["google_rating_count"] = gym_doc.get("google_rating_count")
    return gym


@router.get("/search/nearby")
async def search_nearby_gyms(
    q: str = Query("gym", description="Search query"),
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: int = Query(5000, ge=500, le=50000, description="Radius in meters"),
):
    """Search for gyms near a location using Google Places API."""
    from app.config import get_settings
    settings = get_settings()

    if not settings.GOOGLE_PLACES_API_KEY:
        # Fallback: return gyms from our database sorted by proximity
        db = get_db()
        query = {
            "location": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                    "$maxDistance": radius,
                }
            }
        }
        try:
            gyms = await db.gyms.find(query).limit(20).to_list(20)
            return {"results": [await _enrich_gym(g) for g in gyms], "source": "database"}
        except Exception:
            gyms = await db.gyms.find().limit(20).to_list(20)
            return {"results": [await _enrich_gym(g) for g in gyms], "source": "database"}

    # Use Google Places Text Search
    import httpx
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.currentOpeningHours,places.businessStatus,places.types",
    }
    body = {
        "textQuery": q,
        "maxResultCount": 20,
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": float(radius),
            }
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://places.googleapis.com/v1/places:searchText",
                json=body, headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Google Places API error: {str(e)}")

    results = []
    for p in data.get("places", []):
        results.append({
            "google_place_id": p.get("id"),
            "name": p.get("displayName", {}).get("text", "Unknown"),
            "address": p.get("formattedAddress", ""),
            "lat": p.get("location", {}).get("latitude"),
            "lng": p.get("location", {}).get("longitude"),
            "rating": p.get("rating"),
            "rating_count": p.get("userRatingCount"),
            "is_open": p.get("currentOpeningHours", {}).get("openNow"),
            "business_status": p.get("businessStatus"),
            "types": p.get("types", []),
            "source": "google",
        })

    return {"results": results, "source": "google_places", "count": len(results)}


@router.post("/import-google")
async def import_google_place(
    place: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    """Import a gym from Google Places search results into our database."""
    db = get_db()

    # Check if already imported
    existing = await db.gyms.find_one({"google_place_id": place.get("google_place_id")})
    if existing:
        return await _enrich_gym(existing)

    gym_doc = {
        "name": place.get("name", "Unknown Gym"),
        "address": place.get("address", ""),
        "gym_type": "gym",
        "amenities": [],
        "description": "",
        "google_place_id": place.get("google_place_id"),
        "google_rating": place.get("rating"),
        "google_rating_count": place.get("rating_count"),
        "created_by": current_user["_id"],
        "created_at": datetime.utcnow(),
    }
    if place.get("lat") and place.get("lng"):
        gym_doc["location"] = {
            "type": "Point",
            "coordinates": [place["lng"], place["lat"]],
        }

    result = await db.gyms.insert_one(gym_doc)
    gym_doc["_id"] = result.inserted_id
    return await _enrich_gym(gym_doc)


@router.post("/", status_code=201)
async def create_gym(gym_data: GymCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    gym_doc = {
        "name": gym_data.name,
        "address": gym_data.address,
        "gym_type": gym_data.gym_type.value,
        "amenities": gym_data.amenities,
        "description": gym_data.description,
        "created_by": current_user["_id"],
        "created_at": datetime.utcnow(),
    }
    if gym_data.latitude is not None and gym_data.longitude is not None:
        gym_doc["location"] = {
            "type": "Point",
            "coordinates": [gym_data.longitude, gym_data.latitude],
        }
    result = await db.gyms.insert_one(gym_doc)
    gym_doc["_id"] = result.inserted_id
    return await _enrich_gym(gym_doc)


@router.get("/")
async def list_gyms(
    search: Optional[str] = None,
    gym_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_db()
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if gym_type:
        query["gym_type"] = gym_type

    cursor = db.gyms.find(query).sort("name", 1).skip(skip).limit(limit)
    gyms = await cursor.to_list(length=limit)
    enriched = [await _enrich_gym(g) for g in gyms]
    total = await db.gyms.count_documents(query)
    return {"gyms": enriched, "total": total}


@router.get("/{gym_id}")
async def get_gym(gym_id: str):
    db = get_db()
    gym = await db.gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")
    return await _enrich_gym(gym)


@router.put("/{gym_id}")
async def update_gym(
    gym_id: str,
    update_data: GymUpdate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    update_fields = update_data.model_dump(exclude_none=True)
    if "latitude" in update_fields and "longitude" in update_fields:
        update_fields["location"] = {
            "type": "Point",
            "coordinates": [update_fields.pop("longitude"), update_fields.pop("latitude")],
        }
    else:
        update_fields.pop("latitude", None)
        update_fields.pop("longitude", None)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.gyms.update_one(
        {"_id": ObjectId(gym_id)},
        {"$set": update_fields},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Gym not found")
    return {"message": "Gym updated"}


# --- Popular Times ---

@router.get("/{gym_id}/popular-times")
async def get_popular_times(gym_id: str):
    """
    Get popular times for a gym, aggregated from historical crowd reports.
    Returns busyness by hour for each day of the week.
    """
    db = get_db()
    gym = await db.gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    # Check for pre-computed popular times first
    popular_times = await db.popular_times.find_one({"gym_id": gym_id})

    data_source = "user_reports"

    if popular_times and popular_times.get("days"):
        days_data = popular_times["days"]
    else:
        # Aggregate from crowd reports over the past 30 days
        cutoff = datetime.utcnow() - timedelta(days=30)
        pipeline = [
            {"$match": {"gym_id": gym_id, "timestamp": {"$gte": cutoff}}},
            {"$project": {
                "busy_level": 1,
                "day_of_week": {"$dayOfWeek": "$timestamp"},  # 1=Sun, 7=Sat
                "hour": {"$hour": "$timestamp"},
            }},
            {"$group": {
                "_id": {"day": "$day_of_week", "hour": "$hour"},
                "avg_level": {"$avg": "$busy_level"},
                "count": {"$sum": 1},
            }},
            {"$sort": {"_id.day": 1, "_id.hour": 1}},
        ]
        results = await db.crowd_reports.aggregate(pipeline).to_list(200)

        if results:
            # Build the days structure from user reports
            days_data = []
            for day_idx in range(7):
                # MongoDB dayOfWeek: 1=Sunday...7=Saturday → convert to 0=Monday...6=Sunday
                mongo_day = ((day_idx + 1) % 7) + 1
                hours = []
                for hour in range(24):
                    match = next(
                        (r for r in results if r["_id"]["day"] == mongo_day and r["_id"]["hour"] == hour),
                        None,
                    )
                    level = round(match["avg_level"], 1) if match else 0
                    hours.append({"hour": hour, "level": level})
                days_data.append({
                    "day_of_week": day_idx,
                    "day_name": DAY_NAMES[day_idx],
                    "hours": hours,
                })
        else:
            # No user data at all — fall back to Google estimated patterns
            place_id = gym.get("google_place_id")
            google_days = await fetch_google_popular_times(place_id)
            if google_days:
                days_data = google_days
                data_source = "google_estimated"
            else:
                # Generate empty structure
                days_data = []
                for day_idx in range(7):
                    days_data.append({
                        "day_of_week": day_idx,
                        "day_name": DAY_NAMES[day_idx],
                        "hours": [{"hour": h, "level": 0} for h in range(24)],
                    })

    # Get current hour info
    now = datetime.utcnow()
    current_day_idx = now.weekday()
    current_hour = now.hour
    current_hour_level = None
    current_day_name = DAY_NAMES[current_day_idx]

    for day in days_data:
        if day["day_of_week"] == current_day_idx:
            for h in day["hours"]:
                if h["hour"] == current_hour:
                    current_hour_level = h["level"]
                    break

    return {
        "gym_id": gym_id,
        "gym_name": gym["name"],
        "days": days_data,
        "current_hour_level": current_hour_level,
        "current_day": current_day_name,
        "current_hour": current_hour,
        "data_source": data_source,
    }


# --- Crowd Reports ---

@router.post("/{gym_id}/crowd-reports", status_code=201)
async def submit_crowd_report(
    gym_id: str,
    report: CrowdReportCreate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    gym = await db.gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    report_doc = {
        "gym_id": gym_id,
        "user_id": current_user["_id"],
        "user_display_name": current_user["display_name"],
        "busy_level": report.busy_level.value,
        "notes": report.notes,
        "timestamp": datetime.utcnow(),
    }
    result = await db.crowd_reports.insert_one(report_doc)
    report_doc["_id"] = result.inserted_id
    doc = serialize_doc(report_doc)
    doc["busy_level_label"] = BUSY_LEVEL_LABELS[report.busy_level.value]
    return doc


@router.get("/{gym_id}/crowd-reports")
async def get_crowd_reports(
    gym_id: str,
    hours: int = Query(2, ge=1, le=24),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_db()
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    cursor = db.crowd_reports.find({
        "gym_id": gym_id,
        "timestamp": {"$gte": cutoff},
    }).sort("timestamp", -1).limit(limit)

    reports = await cursor.to_list(length=limit)
    result = []
    for r in reports:
        doc = serialize_doc(r)
        doc["busy_level_label"] = BUSY_LEVEL_LABELS.get(r["busy_level"], "Unknown")
        result.append(doc)
    return {"reports": result, "count": len(result)}


# --- User saved gyms ---

@router.post("/{gym_id}/save")
async def save_gym(gym_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    gym = await db.gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$addToSet": {"saved_gyms": gym_id}},
    )
    return {"message": "Gym saved"}


@router.delete("/{gym_id}/save")
async def unsave_gym(gym_id: str, current_user: dict = Depends(get_current_user)):
    await get_db().users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$pull": {"saved_gyms": gym_id}},
    )
    return {"message": "Gym removed from saved"}


# --- Google Places Integration ---

@router.get("/google/search")
async def google_search_places(
    q: str = Query(..., min_length=2, description="Search query"),
    lat: Optional[float] = None,
    lng: Optional[float] = None,
):
    """Search Google Places for gyms/courts. Requires GOOGLE_PLACES_API_KEY."""
    from app.config import get_settings
    if not get_settings().GOOGLE_PLACES_API_KEY:
        return {"results": [], "message": "Google Places API key not configured. Add GOOGLE_PLACES_API_KEY to .env"}

    result = await search_place(q, lat, lng)
    return {"results": [result] if result else [], "source": "google_places"}


@router.post("/{gym_id}/link-google")
async def link_gym_google(gym_id: str, current_user: dict = Depends(get_current_user)):
    """Auto-link a gym to its Google Place ID by searching its name + address."""
    db = get_db()
    gym = await db.gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    if gym.get("google_place_id"):
        return {"message": "Already linked", "place_id": gym["google_place_id"]}

    place_id = await link_gym_to_google(gym, db)
    if place_id:
        return {"message": "Linked to Google Places", "place_id": place_id}
    return {"message": "Could not find matching Google Place"}
