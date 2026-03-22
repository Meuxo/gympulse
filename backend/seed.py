"""
Seed script — populates GymPulse with real gyms, basketball courts,
sample workouts, wearable data, crowd reports, and popular times.
Run: python seed.py
"""

import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
from dotenv import load_dotenv
import os
import random
import math

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "gympulse")

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def generate_popular_times(gym_type: str) -> list[dict]:
    """
    Generate realistic popular times patterns.
    Gym: peaks at 6-8am and 5-7pm weekdays, midday weekends.
    Basketball: peaks in evenings and weekends.
    """
    days = []
    for day_idx in range(7):
        is_weekend = day_idx >= 5
        hours = []
        for hour in range(24):
            if gym_type in ("gym", "both"):
                if is_weekend:
                    # Weekend gym pattern: 9am-2pm peak
                    if 6 <= hour <= 8:
                        base = random.uniform(1.5, 2.5)
                    elif 9 <= hour <= 13:
                        base = random.uniform(3.0, 4.5)
                    elif 14 <= hour <= 17:
                        base = random.uniform(2.5, 3.5)
                    elif 18 <= hour <= 20:
                        base = random.uniform(2.0, 3.0)
                    elif 5 <= hour <= 21:
                        base = random.uniform(1.5, 2.5)
                    else:
                        base = random.uniform(0, 1.0)
                else:
                    # Weekday gym pattern: 6-8am and 5-7pm peaks
                    if 5 <= hour <= 7:
                        base = random.uniform(3.0, 4.5)
                    elif 8 <= hour <= 10:
                        base = random.uniform(2.0, 3.0)
                    elif 11 <= hour <= 13:
                        base = random.uniform(2.5, 3.5)
                    elif 14 <= hour <= 16:
                        base = random.uniform(2.0, 2.5)
                    elif 17 <= hour <= 19:
                        base = random.uniform(3.5, 5.0)
                    elif 20 <= hour <= 21:
                        base = random.uniform(2.5, 3.5)
                    elif hour == 22:
                        base = random.uniform(1.5, 2.0)
                    else:
                        base = random.uniform(0, 1.0)
            else:
                # Basketball court pattern: afternoon/evening
                if is_weekend:
                    if 10 <= hour <= 14:
                        base = random.uniform(3.0, 4.5)
                    elif 15 <= hour <= 19:
                        base = random.uniform(3.5, 5.0)
                    elif 20 <= hour <= 21:
                        base = random.uniform(2.5, 3.5)
                    elif 8 <= hour <= 22:
                        base = random.uniform(1.5, 2.5)
                    else:
                        base = random.uniform(0, 0.5)
                else:
                    if 16 <= hour <= 19:
                        base = random.uniform(3.0, 4.5)
                    elif 20 <= hour <= 21:
                        base = random.uniform(2.0, 3.5)
                    elif 12 <= hour <= 15:
                        base = random.uniform(1.5, 2.5)
                    elif 7 <= hour <= 22:
                        base = random.uniform(0.5, 1.5)
                    else:
                        base = random.uniform(0, 0.5)

            level = max(0, min(5, round(base, 1)))
            hours.append({"hour": hour, "level": level})

        days.append({
            "day_of_week": day_idx,
            "day_name": DAY_NAMES[day_idx],
            "hours": hours,
        })
    return days


# ======================================================
# REAL GYM DATA
# ======================================================

REAL_GYMS = [
    # --- Major gym chains ---
    {"name": "Planet Fitness - Times Square", "address": "333 W 42nd St, New York, NY 10036", "lat": 40.7577, "lng": -73.9918, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "massage chairs", "hydromassage"]},
    {"name": "Planet Fitness - Downtown Brooklyn", "address": "525 Fulton St, Brooklyn, NY 11201", "lat": 40.6872, "lng": -73.9836, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Equinox Hudson Yards", "address": "35 Hudson Yards, New York, NY 10001", "lat": 40.7539, "lng": -74.0014, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "sauna", "spa", "classes", "personal training"]},
    {"name": "Equinox Flatiron", "address": "897 Broadway, New York, NY 10003", "lat": 40.7389, "lng": -73.9901, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "sauna", "spa", "classes"]},
    {"name": "Crunch Fitness - 34th Street", "address": "404 W 34th St, New York, NY 10001", "lat": 40.7524, "lng": -73.9956, "gym_type": "gym",
     "amenities": ["weights", "cardio", "classes", "personal training", "sauna"]},
    {"name": "Crunch Fitness - Bushwick", "address": "1500 Broadway, Brooklyn, NY 11207", "lat": 40.6888, "lng": -73.9131, "gym_type": "gym",
     "amenities": ["weights", "cardio", "classes", "personal training"]},
    {"name": "LA Fitness - Garden City", "address": "987 Stewart Ave, Garden City, NY 11530", "lat": 40.7262, "lng": -73.6341, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "racquetball", "sauna"]},
    {"name": "24 Hour Fitness - Downtown LA", "address": "735 S Figueroa St, Los Angeles, CA 90017", "lat": 34.0476, "lng": -118.2599, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "sauna", "basketball", "classes"]},
    {"name": "24 Hour Fitness - San Francisco", "address": "350 Bay St, San Francisco, CA 94133", "lat": 37.8060, "lng": -122.4142, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "sauna", "classes"]},
    {"name": "Gold's Gym - Venice Beach", "address": "360 Hampton Dr, Venice, CA 90291", "lat": 33.9925, "lng": -118.4714, "gym_type": "gym",
     "amenities": ["weights", "cardio", "outdoor area", "classes", "personal training"]},
    {"name": "Gold's Gym - Arlington", "address": "4301 S Fairfax Dr, Arlington, VA 22203", "lat": 38.8535, "lng": -77.1015, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "classes", "personal training"]},
    {"name": "YMCA - Vanderbilt", "address": "224 E 47th St, New York, NY 10017", "lat": 40.7539, "lng": -73.9725, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes", "track"]},
    {"name": "YMCA - Bedford-Stuyvesant", "address": "1121 Bedford Ave, Brooklyn, NY 11216", "lat": 40.6870, "lng": -73.9533, "gym_type": "both",
     "amenities": ["weights", "cardio", "basketball", "pool", "classes"]},
    {"name": "Life Time Fitness - Chestnut Hill", "address": "300 Boylston St, Chestnut Hill, MA 02467", "lat": 42.3221, "lng": -71.1671, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "rock climbing", "spa", "cafe"]},
    {"name": "Orangetheory Fitness - Chelsea", "address": "148 W 23rd St, New York, NY 10011", "lat": 40.7435, "lng": -73.9966, "gym_type": "gym",
     "amenities": ["cardio", "HIIT", "heart rate monitoring", "classes"]},
    {"name": "CrossFit Solace", "address": "38 W 14th St, New York, NY 10011", "lat": 40.7367, "lng": -73.9963, "gym_type": "gym",
     "amenities": ["crossfit", "weightlifting", "classes", "open gym"]},
    {"name": "Blink Fitness - Flatbush", "address": "2148 Nostrand Ave, Brooklyn, NY 11210", "lat": 40.6310, "lng": -73.9466, "gym_type": "gym",
     "amenities": ["weights", "cardio", "clean locker rooms"]},
    {"name": "Blink Fitness - 125th Street", "address": "301 W 125th St, New York, NY 10027", "lat": 40.8092, "lng": -73.9549, "gym_type": "gym",
     "amenities": ["weights", "cardio", "clean locker rooms"]},
    {"name": "Anytime Fitness - Astoria", "address": "31-11 Broadway, Astoria, NY 11106", "lat": 40.7629, "lng": -73.9247, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access", "personal training"]},
    {"name": "Chelsea Piers Fitness", "address": "62 Chelsea Piers, New York, NY 10011", "lat": 40.7471, "lng": -74.0087, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "rock climbing", "boxing", "track"]},

    # --- Basketball courts ---
    {"name": "Rucker Park", "address": "155th St & Frederick Douglass Blvd, New York, NY 10039", "lat": 40.8293, "lng": -73.9367, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "bleachers", "lights", "legendary pickup games"]},
    {"name": "The Cage - West 4th Street Courts", "address": "181 W 4th St, New York, NY 10014", "lat": 40.7324, "lng": -74.0002, "gym_type": "basketball_court",
     "amenities": ["outdoor court", "lights", "famous pickup games"]},
    {"name": "Brooklyn Bridge Park - Pier 2", "address": "Pier 2, Brooklyn Bridge Park, Brooklyn, NY 11201", "lat": 40.6963, "lng": -73.9976, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "waterfront", "lights", "5 full courts"]},
    {"name": "Venice Beach Basketball Courts", "address": "1800 Ocean Front Walk, Venice, CA 90291", "lat": 33.9850, "lng": -118.4730, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "beach", "pickup games", "lights"]},
    {"name": "Lincoln Park Courts", "address": "2045 N Lincoln Park W, Chicago, IL 60614", "lat": 41.9200, "lng": -87.6355, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "park setting"]},
    {"name": "Hoop Heaven - Kearny", "address": "131 Passaic Ave, Kearny, NJ 07032", "lat": 40.7535, "lng": -74.1210, "gym_type": "basketball_court",
     "amenities": ["indoor courts", "leagues", "open gym", "training"]},
    {"name": "Dyckman Park Basketball Courts", "address": "Nagle Ave & Academy St, New York, NY 10034", "lat": 40.8645, "lng": -73.9269, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "tournament site", "lights", "bleachers"]},
    {"name": "Cromwell Park Courts", "address": "5801 Cromwell Dr, Capitol Heights, MD 20743", "lat": 38.8869, "lng": -76.8958, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "parking"]},
    {"name": "Geraldine Ferraro Park Courts", "address": "30-60 21st St, Astoria, NY 11102", "lat": 40.7710, "lng": -73.9237, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "park setting"]},
    {"name": "LA Fitness Basketball - Rego Park", "address": "9702 Queens Blvd, Rego Park, NY 11374", "lat": 40.7280, "lng": -73.8590, "gym_type": "both",
     "amenities": ["indoor basketball", "weights", "cardio", "pool"]},
]


async def seed():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]

    # Clear existing data
    for col in ["users", "workouts", "wearable_syncs", "gyms", "crowd_reports", "basketball_reports", "popular_times"]:
        await db[col].drop()
    print("Cleared existing data.")

    # --- Users ---
    users = []
    user_data = [
        {"email": "demo@gympulse.com", "display_name": "Demo User", "password": "password123"},
        {"email": "jane@gympulse.com", "display_name": "Jane Smith", "password": "password123"},
        {"email": "mike@gympulse.com", "display_name": "Mike Johnson", "password": "password123"},
        {"email": "alex@gympulse.com", "display_name": "Alex Rivera", "password": "password123"},
        {"email": "sarah@gympulse.com", "display_name": "Sarah Chen", "password": "password123"},
    ]
    for u in user_data:
        result = await db.users.insert_one({
            "email": u["email"],
            "password_hash": hash_password(u["password"]),
            "display_name": u["display_name"],
            "saved_gyms": [],
            "wearable_connections": {},
            "preferences": {"units": "imperial", "default_gym_id": None, "notifications_enabled": True},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
        users.append(str(result.inserted_id))
    print(f"Created {len(users)} users.")

    # --- Real Gyms ---
    gym_ids = []
    bball_gym_ids = []
    for g in REAL_GYMS:
        doc = {
            "name": g["name"],
            "address": g["address"],
            "gym_type": g["gym_type"],
            "location": {"type": "Point", "coordinates": [g["lng"], g["lat"]]},
            "amenities": g["amenities"],
            "description": None,
            "created_by": users[0],
            "created_at": datetime.utcnow(),
        }
        result = await db.gyms.insert_one(doc)
        gid = str(result.inserted_id)
        gym_ids.append(gid)
        if g["gym_type"] in ("basketball_court", "both"):
            bball_gym_ids.append(gid)

    # Save first 5 gyms for demo user
    await db.users.update_one(
        {"email": "demo@gympulse.com"},
        {"$set": {"saved_gyms": gym_ids[:5]}},
    )
    print(f"Created {len(gym_ids)} real gyms and courts.")

    # --- Popular Times for every gym ---
    for i, gid in enumerate(gym_ids):
        gym_type = REAL_GYMS[i]["gym_type"]
        await db.popular_times.insert_one({
            "gym_id": gid,
            "days": generate_popular_times(gym_type),
            "updated_at": datetime.utcnow(),
        })
    print(f"Generated popular times for {len(gym_ids)} locations.")

    # --- Crowd reports (spread over last 2 hours for recency) ---
    report_count = 0
    for gid in gym_ids:
        num_reports = random.randint(3, 12)
        for _ in range(num_reports):
            user_idx = random.randint(0, len(users) - 1)
            minutes_ago = random.randint(5, 120)
            await db.crowd_reports.insert_one({
                "gym_id": gid,
                "user_id": users[user_idx],
                "user_display_name": user_data[user_idx]["display_name"],
                "busy_level": random.randint(1, 5),
                "notes": random.choice([None, None, None, "Pretty chill", "Getting crowded", "Full house", "Just opened", "About to close"]),
                "timestamp": datetime.utcnow() - timedelta(minutes=minutes_ago),
            })
            report_count += 1

    # Also generate historical reports for popular times aggregation
    for gid in gym_ids[:10]:
        for days_ago in range(1, 15):
            num_reports = random.randint(2, 8)
            for _ in range(num_reports):
                user_idx = random.randint(0, len(users) - 1)
                hour = random.randint(6, 22)
                ts = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 3))
                ts = ts.replace(hour=hour, minute=random.randint(0, 59))
                await db.crowd_reports.insert_one({
                    "gym_id": gid,
                    "user_id": users[user_idx],
                    "user_display_name": user_data[user_idx]["display_name"],
                    "busy_level": random.randint(1, 5),
                    "notes": None,
                    "timestamp": ts,
                })
                report_count += 1
    print(f"Created {report_count} crowd reports.")

    # --- Basketball reports ---
    bball_count = 0
    for gid in bball_gym_ids:
        for minutes_ago in [10, 25, 45, 70, 100, 130]:
            if random.random() < 0.6:
                user_idx = random.randint(0, len(users) - 1)
                await db.basketball_reports.insert_one({
                    "gym_id": gid,
                    "user_id": users[user_idx],
                    "user_display_name": user_data[user_idx]["display_name"],
                    "player_count": random.randint(2, 24),
                    "photo_url": None,
                    "notes": random.choice([None, "Good runs", "Full court 5v5", "Just shooting around", "Next game winners", "3v3 half court"]),
                    "timestamp": datetime.utcnow() - timedelta(minutes=minutes_ago),
                })
                bball_count += 1
    print(f"Created {bball_count} basketball reports.")

    # --- Workouts (demo user, last 30 days) ---
    workout_templates = [
        {"title": "Morning Push Day", "type": "strength", "muscles": ["chest", "shoulders", "triceps"],
         "exercises": [
             {"name": "Bench Press", "sets": 4, "reps": 8, "weight": 185},
             {"name": "Overhead Press", "sets": 3, "reps": 10, "weight": 95},
             {"name": "Incline Dumbbell Press", "sets": 3, "reps": 10, "weight": 65},
             {"name": "Tricep Pushdowns", "sets": 3, "reps": 12, "weight": 50},
             {"name": "Lateral Raises", "sets": 3, "reps": 15, "weight": 20},
         ], "duration": 55, "calories": 320},
        {"title": "Leg Day", "type": "strength", "muscles": ["legs", "glutes"],
         "exercises": [
             {"name": "Barbell Squat", "sets": 4, "reps": 6, "weight": 225},
             {"name": "Romanian Deadlift", "sets": 3, "reps": 10, "weight": 155},
             {"name": "Leg Press", "sets": 3, "reps": 12, "weight": 320},
             {"name": "Walking Lunges", "sets": 3, "reps": 12, "weight": 40},
             {"name": "Calf Raises", "sets": 4, "reps": 15, "weight": 135},
         ], "duration": 60, "calories": 400},
        {"title": "Pull Day", "type": "strength", "muscles": ["back", "biceps"],
         "exercises": [
             {"name": "Deadlift", "sets": 4, "reps": 5, "weight": 275},
             {"name": "Pull-ups", "sets": 3, "reps": 8, "weight": 0},
             {"name": "Barbell Rows", "sets": 3, "reps": 10, "weight": 135},
             {"name": "Face Pulls", "sets": 3, "reps": 15, "weight": 30},
             {"name": "Bicep Curls", "sets": 3, "reps": 12, "weight": 35},
         ], "duration": 50, "calories": 350},
        {"title": "HIIT Session", "type": "hiit", "muscles": ["full_body", "cardio"],
         "exercises": [
             {"name": "Burpees", "sets": 4, "reps": 15},
             {"name": "Mountain Climbers", "sets": 4, "reps": 20, "duration": 60},
             {"name": "Box Jumps", "sets": 4, "reps": 12},
             {"name": "Battle Ropes", "duration": 180},
         ], "duration": 30, "calories": 450},
        {"title": "Basketball Pickup", "type": "sports", "muscles": ["full_body", "cardio"],
         "exercises": [
             {"name": "5v5 Full Court", "duration": 3600},
             {"name": "Shooting Drills", "duration": 900},
         ], "duration": 90, "calories": 600},
        {"title": "5K Run", "type": "cardio", "muscles": ["legs", "cardio"],
         "exercises": [
             {"name": "Running", "distance": 3.1, "duration": 1500, "calories": 350},
         ], "duration": 25, "calories": 350},
    ]

    workout_count = 0
    for days_ago in range(30):
        if random.random() < 0.35:
            continue
        template = random.choice(workout_templates)
        workout_date = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(6, 18))
        await db.workouts.insert_one({
            "user_id": users[0],
            "title": template["title"],
            "workout_type": template["type"],
            "muscle_groups": template["muscles"],
            "exercises": template["exercises"],
            "date": workout_date,
            "total_duration": template["duration"],
            "total_calories": template["calories"],
            "notes": None,
            "created_at": workout_date,
            "updated_at": workout_date,
        })
        workout_count += 1
    print(f"Created {workout_count} workouts.")

    # --- Wearable data (demo user, last 14 days) ---
    sync_count = 0
    for days_ago in range(14):
        date = datetime.utcnow() - timedelta(days=days_ago)
        date = date.replace(hour=23, minute=59, second=0)
        metrics = [
            ("steps", random.randint(4000, 16000), "steps"),
            ("heart_rate", random.randint(58, 88), "bpm"),
            ("calories_burned", random.randint(1700, 3000), "kcal"),
            ("sleep_duration", round(random.uniform(5.0, 9.5), 1), "hours"),
            ("active_minutes", random.randint(15, 95), "minutes"),
            ("distance", round(random.uniform(1.5, 9.0), 2), "miles"),
        ]
        for metric_type, value, unit in metrics:
            await db.wearable_syncs.insert_one({
                "user_id": users[0],
                "provider": random.choice(["fitbit", "apple_health"]),
                "metric_type": metric_type,
                "value": value,
                "unit": unit,
                "recorded_at": date,
                "synced_at": date,
                "raw_data": None,
            })
            sync_count += 1
    print(f"Created {sync_count} wearable sync records.")

    # --- Indexes ---
    await db.users.create_index("email", unique=True)
    await db.workouts.create_index([("user_id", 1), ("date", -1)])
    await db.wearable_syncs.create_index([("user_id", 1), ("provider", 1), ("synced_at", -1)])
    await db.gyms.create_index([("location", "2dsphere")])
    await db.gyms.create_index("name")
    await db.crowd_reports.create_index([("gym_id", 1), ("timestamp", -1)])
    await db.basketball_reports.create_index([("gym_id", 1), ("timestamp", -1)])
    await db.popular_times.create_index("gym_id", unique=True)

    print("\n=== Seeding complete! ===")
    print(f"Demo account: demo@gympulse.com / password123")
    print(f"Total: {len(gym_ids)} gyms, {len(bball_gym_ids)} basketball locations")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
