from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from bson import ObjectId
from app.database import get_db
from app.auth.jwt import get_current_user
from app.utils.helpers import serialize_doc, serialize_docs, weighted_average_busy_level
from app.models.gym import BUSY_LEVEL_LABELS

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def dashboard_summary(current_user: dict = Depends(get_current_user)):
    """Get a combined dashboard summary for the current user."""
    db = get_db()
    user_id = current_user["_id"]
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # --- Today's workouts ---
    today_workouts = await db.workouts.find({
        "user_id": user_id,
        "date": {"$gte": today_start, "$lt": today_end},
    }).to_list(20)

    workout_summary = {
        "count": len(today_workouts),
        "total_duration": sum(w.get("total_duration", 0) or 0 for w in today_workouts),
        "total_calories": sum(w.get("total_calories", 0) or 0 for w in today_workouts),
        "workouts": serialize_docs(today_workouts),
    }

    # --- Wearable daily summary ---
    wearable_pipeline = [
        {"$match": {
            "user_id": user_id,
            "recorded_at": {"$gte": today_start, "$lt": today_end},
        }},
        {"$group": {
            "_id": "$metric_type",
            "total": {"$sum": "$value"},
            "avg": {"$avg": "$value"},
        }},
    ]
    wearable_results = await db.wearable_syncs.aggregate(wearable_pipeline).to_list(20)
    wearable_summary = {}
    for r in wearable_results:
        metric = r["_id"]
        if metric in ("steps", "calories_burned", "active_minutes", "distance"):
            wearable_summary[metric] = r["total"]
        elif metric == "heart_rate":
            wearable_summary["heart_rate_avg"] = round(r["avg"], 1)
        elif metric == "sleep_duration":
            wearable_summary["sleep_duration"] = r["total"]

    # --- Saved gym crowd levels ---
    saved_gym_ids = current_user.get("saved_gyms", [])
    gym_reports = []
    for gym_id in saved_gym_ids[:10]:  # Limit to 10 saved gyms
        gym = await db.gyms.find_one({"_id": ObjectId(gym_id)})
        if not gym:
            continue
        cutoff = datetime.utcnow() - timedelta(hours=2)
        reports = await db.crowd_reports.find({
            "gym_id": gym_id,
            "timestamp": {"$gte": cutoff},
        }).to_list(50)

        busy_level = weighted_average_busy_level(reports)
        gym_info = {
            "gym_id": gym_id,
            "name": gym["name"],
            "gym_type": gym.get("gym_type", "gym"),
            "current_busy_level": busy_level,
            "busy_level_label": BUSY_LEVEL_LABELS.get(round(busy_level), "Unknown") if busy_level else None,
            "recent_reports_count": len(reports),
        }
        gym_reports.append(gym_info)

    # --- Recent basketball reports for saved courts ---
    basketball_summary = []
    for gym_id in saved_gym_ids[:10]:
        gym = await db.gyms.find_one({"_id": ObjectId(gym_id)})
        if not gym or gym.get("gym_type") not in ("basketball_court", "both"):
            continue
        cutoff = datetime.utcnow() - timedelta(hours=4)
        bball_reports = await db.basketball_reports.find({
            "gym_id": gym_id,
            "timestamp": {"$gte": cutoff},
        }).sort("timestamp", -1).to_list(5)

        if bball_reports:
            avg_players = sum(r["player_count"] for r in bball_reports) / len(bball_reports)
            basketball_summary.append({
                "gym_id": gym_id,
                "name": gym["name"],
                "avg_player_count": round(avg_players, 1),
                "latest_report": serialize_doc(bball_reports[0]),
                "reports_count": len(bball_reports),
            })

    return {
        "date": today_start.strftime("%Y-%m-%d"),
        "workouts": workout_summary,
        "wearables": wearable_summary,
        "gyms": gym_reports,
        "basketball": basketball_summary,
    }
