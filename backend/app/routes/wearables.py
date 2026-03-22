from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
import httpx
import base64
from app.database import get_db
from app.auth.jwt import get_current_user
from app.config import get_settings
from app.models.wearable import (
    WearableProvider, MetricType,
    WearableSyncCreate, WearableSyncBatch,
)
from app.utils.helpers import serialize_doc, serialize_docs

router = APIRouter(prefix="/wearables", tags=["Wearables"])
settings = get_settings()

FITBIT_AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
FITBIT_TOKEN_URL = "https://api.fitbit.com/oauth2/token"
FITBIT_API_BASE = "https://api.fitbit.com"
FITBIT_SCOPES = "activity heartrate sleep profile weight nutrition"


# --- Data sync endpoints ---

@router.post("/sync")
async def sync_data(sync_data: WearableSyncCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    doc = {
        "user_id": current_user["_id"],
        "provider": sync_data.provider.value,
        "metric_type": sync_data.metric_type.value,
        "value": sync_data.value,
        "unit": sync_data.unit,
        "recorded_at": sync_data.recorded_at,
        "synced_at": datetime.utcnow(),
        "raw_data": sync_data.raw_data,
    }
    result = await db.wearable_syncs.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@router.post("/sync/batch")
async def sync_batch(batch: WearableSyncBatch, current_user: dict = Depends(get_current_user)):
    db = get_db()
    docs = []
    for item in batch.data:
        docs.append({
            "user_id": current_user["_id"],
            "provider": batch.provider.value,
            "metric_type": item.metric_type.value,
            "value": item.value,
            "unit": item.unit,
            "recorded_at": item.recorded_at,
            "synced_at": datetime.utcnow(),
            "raw_data": item.raw_data,
        })
    if docs:
        await db.wearable_syncs.insert_many(docs)
    return {"message": f"Synced {len(docs)} records", "count": len(docs)}


@router.get("/data")
async def get_sync_data(
    current_user: dict = Depends(get_current_user),
    provider: Optional[WearableProvider] = None,
    metric_type: Optional[MetricType] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    db = get_db()
    query = {"user_id": current_user["_id"]}
    if provider:
        query["provider"] = provider.value
    if metric_type:
        query["metric_type"] = metric_type.value
    if date_from or date_to:
        query["recorded_at"] = {}
        if date_from:
            query["recorded_at"]["$gte"] = date_from
        if date_to:
            query["recorded_at"]["$lte"] = date_to

    cursor = db.wearable_syncs.find(query).sort("recorded_at", -1).skip(skip).limit(limit)
    data = await cursor.to_list(length=limit)
    return {"data": serialize_docs(data), "count": len(data)}


@router.get("/daily-summary")
async def daily_summary(
    current_user: dict = Depends(get_current_user),
    date: Optional[str] = None,
):
    db = get_db()
    if date:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        target_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    next_day = target_date + timedelta(days=1)

    pipeline = [
        {"$match": {
            "user_id": current_user["_id"],
            "recorded_at": {"$gte": target_date, "$lt": next_day},
        }},
        {"$group": {
            "_id": "$metric_type",
            "total": {"$sum": "$value"},
            "avg": {"$avg": "$value"},
            "max": {"$max": "$value"},
            "count": {"$sum": 1},
        }},
    ]
    results = await db.wearable_syncs.aggregate(pipeline).to_list(20)

    summary = {"date": target_date.strftime("%Y-%m-%d")}
    for r in results:
        metric = r["_id"]
        if metric == "steps":
            summary["steps"] = r["total"]
        elif metric == "heart_rate":
            summary["heart_rate_avg"] = round(r["avg"], 1)
        elif metric == "calories_burned":
            summary["calories_burned"] = r["total"]
        elif metric == "sleep_duration":
            summary["sleep_duration"] = r["total"]
        elif metric == "active_minutes":
            summary["active_minutes"] = r["total"]
        elif metric == "distance":
            summary["distance"] = round(r["total"], 2)

    return summary


@router.get("/connections")
async def get_connections(current_user: dict = Depends(get_current_user)):
    """Get the user's current wearable connections."""
    connections = current_user.get("wearable_connections", {})
    result = []
    for provider_id in ["fitbit", "apple_health", "samsung_health"]:
        conn = connections.get(provider_id, {})
        result.append({
            "provider": provider_id,
            "is_connected": conn.get("is_active", False),
            "connected_at": conn.get("connected_at"),
            "last_sync": conn.get("last_sync"),
        })
    return {"connections": result}


# ============================================================
# FITBIT OAUTH2 - Full implementation
# ============================================================

@router.get("/fitbit/authorize")
async def fitbit_authorize(current_user: dict = Depends(get_current_user)):
    """Start Fitbit OAuth2 Authorization Code Grant flow."""
    if not settings.FITBIT_CLIENT_ID:
        return {
            "status": "not_configured",
            "message": "Fitbit integration requires FITBIT_CLIENT_ID and FITBIT_CLIENT_SECRET environment variables.",
            "setup_url": "https://dev.fitbit.com/apps/new",
        }
    # Include user_id in state to map callback to user
    auth_url = (
        f"{FITBIT_AUTH_URL}?"
        f"response_type=code"
        f"&client_id={settings.FITBIT_CLIENT_ID}"
        f"&redirect_uri={settings.FITBIT_REDIRECT_URI}"
        f"&scope={FITBIT_SCOPES.replace(' ', '%20')}"
        f"&state={current_user['_id']}"
        f"&expires_in=604800"
    )
    return {"authorization_url": auth_url, "status": "redirect"}


@router.get("/fitbit/callback")
async def fitbit_callback(code: str, state: str = ""):
    """
    Handle Fitbit OAuth2 callback.
    Exchanges authorization code for access + refresh tokens.
    """
    if not settings.FITBIT_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Fitbit not configured")

    # Exchange code for tokens
    auth_header = base64.b64encode(
        f"{settings.FITBIT_CLIENT_ID}:{settings.FITBIT_CLIENT_SECRET}".encode()
    ).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            FITBIT_TOKEN_URL,
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "client_id": settings.FITBIT_CLIENT_ID,
                "grant_type": "authorization_code",
                "redirect_uri": settings.FITBIT_REDIRECT_URI,
                "code": code,
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Fitbit token exchange failed: {response.text}",
        )

    tokens = response.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    fitbit_user_id = tokens.get("user_id")

    # Store tokens in user document
    if state:
        db = get_db()
        await db.users.update_one(
            {"_id": ObjectId(state)},
            {"$set": {
                "wearable_connections.fitbit": {
                    "provider": "fitbit",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "fitbit_user_id": fitbit_user_id,
                    "connected_at": datetime.utcnow(),
                    "is_active": True,
                },
            }},
        )

    # Redirect back to frontend
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/wearables?connected=fitbit")


@router.post("/fitbit/sync")
async def fitbit_sync_now(current_user: dict = Depends(get_current_user)):
    """Pull latest data from Fitbit API for the connected user."""
    conn = current_user.get("wearable_connections", {}).get("fitbit", {})
    if not conn.get("is_active") or not conn.get("access_token"):
        raise HTTPException(status_code=400, detail="Fitbit not connected")

    access_token = conn["access_token"]
    today = datetime.utcnow().strftime("%Y-%m-%d")
    headers = {"Authorization": f"Bearer {access_token}"}
    records = []
    db = get_db()

    async with httpx.AsyncClient() as client:
        # Activity summary
        resp = await client.get(
            f"{FITBIT_API_BASE}/1/user/-/activities/date/{today}.json",
            headers=headers,
        )
        if resp.status_code == 200:
            summary = resp.json().get("summary", {})
            if "steps" in summary:
                records.append(("steps", summary["steps"], "steps"))
            if "caloriesOut" in summary:
                records.append(("calories_burned", summary["caloriesOut"], "kcal"))
            active = summary.get("fairlyActiveMinutes", 0) + summary.get("veryActiveMinutes", 0)
            if active:
                records.append(("active_minutes", active, "minutes"))
            if "distances" in summary:
                total_dist = sum(d.get("distance", 0) for d in summary["distances"] if d.get("activity") == "total")
                if total_dist:
                    records.append(("distance", total_dist, "miles"))
            if "floors" in summary:
                records.append(("floors_climbed", summary["floors"], "floors"))

        # Heart rate
        resp = await client.get(
            f"{FITBIT_API_BASE}/1/user/-/activities/heart/date/{today}/1d.json",
            headers=headers,
        )
        if resp.status_code == 200:
            hr_data = resp.json().get("activities-heart", [])
            if hr_data and hr_data[0].get("value", {}).get("restingHeartRate"):
                records.append(("heart_rate", hr_data[0]["value"]["restingHeartRate"], "bpm"))

        # Sleep
        resp = await client.get(
            f"{FITBIT_API_BASE}/1.2/user/-/sleep/date/{today}.json",
            headers=headers,
        )
        if resp.status_code == 200:
            sleep_data = resp.json().get("summary", {})
            total_sleep = sleep_data.get("totalMinutesAsleep", 0)
            if total_sleep:
                records.append(("sleep_duration", round(total_sleep / 60, 1), "hours"))

    # Store records
    if records:
        docs = [{
            "user_id": current_user["_id"],
            "provider": "fitbit",
            "metric_type": metric,
            "value": value,
            "unit": unit,
            "recorded_at": datetime.utcnow(),
            "synced_at": datetime.utcnow(),
        } for metric, value, unit in records]
        await db.wearable_syncs.insert_many(docs)

    # Update last sync time
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"wearable_connections.fitbit.last_sync": datetime.utcnow()}},
    )

    return {"message": f"Synced {len(records)} metrics from Fitbit", "metrics": [r[0] for r in records]}


@router.post("/fitbit/refresh")
async def fitbit_refresh(current_user: dict = Depends(get_current_user)):
    """Refresh Fitbit access token."""
    conn = current_user.get("wearable_connections", {}).get("fitbit", {})
    if not conn.get("refresh_token"):
        raise HTTPException(status_code=400, detail="No Fitbit refresh token")

    auth_header = base64.b64encode(
        f"{settings.FITBIT_CLIENT_ID}:{settings.FITBIT_CLIENT_SECRET}".encode()
    ).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            FITBIT_TOKEN_URL,
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": conn["refresh_token"],
            },
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Token refresh failed")

    tokens = response.json()
    db = get_db()
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {
            "wearable_connections.fitbit.access_token": tokens["access_token"],
            "wearable_connections.fitbit.refresh_token": tokens.get("refresh_token", conn["refresh_token"]),
        }},
    )
    return {"message": "Token refreshed"}


# ============================================================
# APPLE HEALTH - Webhook receiver for iOS app push
# ============================================================

@router.post("/apple-health/receive")
async def apple_health_receive(
    data: WearableSyncBatch,
    current_user: dict = Depends(get_current_user),
):
    """
    Receive health data pushed from the iOS companion app.
    Apple HealthKit data must be exported from an iOS device;
    this endpoint accepts the normalized data payload.
    """
    db = get_db()
    docs = []
    for item in data.data:
        docs.append({
            "user_id": current_user["_id"],
            "provider": "apple_health",
            "metric_type": item.metric_type.value,
            "value": item.value,
            "unit": item.unit,
            "recorded_at": item.recorded_at,
            "synced_at": datetime.utcnow(),
            "raw_data": item.raw_data,
        })
    if docs:
        await db.wearable_syncs.insert_many(docs)
        await db.users.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {"$set": {
                "wearable_connections.apple_health": {
                    "provider": "apple_health",
                    "connected_at": datetime.utcnow(),
                    "is_active": True,
                    "last_sync": datetime.utcnow(),
                },
            }},
        )
    return {"message": f"Received {len(docs)} Apple Health records", "count": len(docs)}


@router.get("/apple-health/info")
async def apple_health_info():
    return {
        "provider": "apple_health",
        "method": "device_push",
        "instructions": [
            "Apple Health data syncs from the GymPulse iOS app.",
            "Open the iOS app → Settings → Health → Connect Apple Health.",
            "Grant access to activity, heart rate, sleep, and workout data.",
            "Data syncs automatically when the app is open.",
        ],
        "supported_metrics": ["steps", "heart_rate", "calories_burned", "sleep_duration", "active_minutes", "distance", "workout_session"],
    }


# ============================================================
# SAMSUNG HEALTH
# ============================================================

@router.post("/samsung-health/receive")
async def samsung_health_receive(
    data: WearableSyncBatch,
    current_user: dict = Depends(get_current_user),
):
    """Receive health data from Samsung Health companion app."""
    db = get_db()
    docs = []
    for item in data.data:
        docs.append({
            "user_id": current_user["_id"],
            "provider": "samsung_health",
            "metric_type": item.metric_type.value,
            "value": item.value,
            "unit": item.unit,
            "recorded_at": item.recorded_at,
            "synced_at": datetime.utcnow(),
            "raw_data": item.raw_data,
        })
    if docs:
        await db.wearable_syncs.insert_many(docs)
        await db.users.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {"$set": {
                "wearable_connections.samsung_health": {
                    "provider": "samsung_health",
                    "connected_at": datetime.utcnow(),
                    "is_active": True,
                    "last_sync": datetime.utcnow(),
                },
            }},
        )
    return {"message": f"Received {len(docs)} Samsung Health records", "count": len(docs)}


@router.get("/samsung-health/info")
async def samsung_health_info():
    return {
        "provider": "samsung_health",
        "method": "device_push",
        "instructions": [
            "Samsung Health data syncs from the GymPulse Android app.",
            "Open the app → Settings → Devices → Connect Samsung Health.",
            "Authorize data sharing in the Samsung Health app.",
            "Data syncs automatically via the Health Connect API.",
        ],
        "supported_metrics": ["steps", "heart_rate", "calories_burned", "sleep_duration", "active_minutes", "distance"],
    }
