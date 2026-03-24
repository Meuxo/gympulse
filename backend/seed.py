"""
Seed script — populates GymPulse with real Minnesota gyms, basketball courts,
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
# MINNESOTA GYMS & BASKETBALL COURTS
# ======================================================

REAL_GYMS = [
    # ===================== LIFE TIME FITNESS =====================
    {"name": "Life Time - Eagan", "address": "1565 Thomas Center Dr, Eagan, MN 55122", "lat": 44.8041, "lng": -93.1674, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "rock climbing", "spa", "cafe"]},
    {"name": "Life Time - Plymouth", "address": "18500 Hwy 55, Plymouth, MN 55446", "lat": 45.0234, "lng": -93.4455, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "spa", "classes", "cafe", "rock climbing"]},
    {"name": "Life Time - Woodbury", "address": "750 Globe Dr, Woodbury, MN 55125", "lat": 44.9105, "lng": -92.9239, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "spa", "classes", "cafe"]},
    {"name": "Life Time - Target Center", "address": "600 1st Ave N, Minneapolis, MN 55403", "lat": 44.9795, "lng": -93.2760, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "spa", "classes"]},
    {"name": "Life Time - Bloomington South", "address": "8501 Hudson Rd, Bloomington, MN 55437", "lat": 44.8312, "lng": -93.3139, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "spa", "rock climbing"]},
    {"name": "Life Time - Lakeville", "address": "21125 Icenic Trail, Lakeville, MN 55044", "lat": 44.6497, "lng": -93.2428, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "spa", "cafe"]},
    {"name": "Life Time - St. Louis Park", "address": "5525 Cedar Lake Rd, St. Louis Park, MN 55416", "lat": 44.9603, "lng": -93.3497, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "spa", "classes"]},
    {"name": "Life Time - Fridley", "address": "7007 University Ave NE, Fridley, MN 55432", "lat": 45.0869, "lng": -93.2571, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "spa"]},
    {"name": "Life Time - Savage", "address": "7600 W 131st St, Savage, MN 55378", "lat": 44.7293, "lng": -93.3697, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "rock climbing"]},
    {"name": "Life Time - Maple Grove", "address": "17690 Elm Creek Blvd, Maple Grove, MN 55311", "lat": 45.1102, "lng": -93.4566, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "spa", "cafe"]},
    {"name": "Life Time - Chanhassen", "address": "655 Lotus Dr, Chanhassen, MN 55317", "lat": 44.8582, "lng": -93.5274, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "spa"]},
    {"name": "Life Time - Apple Valley", "address": "14890 Florence Trail, Apple Valley, MN 55124", "lat": 44.7316, "lng": -93.2240, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "spa", "cafe"]},
    {"name": "Life Time - Burnsville", "address": "201 E Travelers Trail, Burnsville, MN 55337", "lat": 44.7660, "lng": -93.2703, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "spa", "classes"]},
    {"name": "Life Time - Roseville", "address": "2480 Fairview Ave N, Roseville, MN 55113", "lat": 45.0139, "lng": -93.1686, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "spa"]},

    # ===================== ANYTIME FITNESS =====================
    {"name": "Anytime Fitness - Uptown", "address": "3418 W Lake St, Minneapolis, MN 55416", "lat": 44.9487, "lng": -93.3110, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - NE Minneapolis", "address": "2706 NE Johnson St, Minneapolis, MN 55418", "lat": 45.0047, "lng": -93.2470, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Roseville", "address": "1767 Lexington Ave N, Roseville, MN 55113", "lat": 45.0153, "lng": -93.1784, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Burnsville", "address": "401 E Travelers Trail, Burnsville, MN 55337", "lat": 44.7641, "lng": -93.2710, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Eden Prairie", "address": "8088 Mitchell Rd, Eden Prairie, MN 55344", "lat": 44.8547, "lng": -93.4564, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Shakopee", "address": "1107 Vierling Dr E, Shakopee, MN 55379", "lat": 44.7736, "lng": -93.5164, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Coon Rapids", "address": "3460 129th Ave NW, Coon Rapids, MN 55448", "lat": 45.1583, "lng": -93.3536, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Mankato", "address": "1850 Adams St, Mankato, MN 56001", "lat": 44.1712, "lng": -94.0031, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Rochester NW", "address": "1340 Salem Rd SW, Rochester, MN 55902", "lat": 44.0074, "lng": -92.4909, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Duluth", "address": "1301 Miller Trunk Hwy, Duluth, MN 55811", "lat": 46.8168, "lng": -92.1367, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - St. Cloud", "address": "4101 W Division St, St. Cloud, MN 56301", "lat": 45.5474, "lng": -94.2229, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Woodbury", "address": "2070 Eagle Creek Ln, Woodbury, MN 55129", "lat": 44.8990, "lng": -92.8925, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Blaine", "address": "12584 Ulysses St NE, Blaine, MN 55434", "lat": 45.1412, "lng": -93.2170, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Cottage Grove", "address": "9409 E Point Douglas Rd S, Cottage Grove, MN 55016", "lat": 44.8270, "lng": -92.9100, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Owatonna", "address": "1265 W Frontage Rd, Owatonna, MN 55060", "lat": 44.0778, "lng": -93.2448, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Winona", "address": "1213 Gilmore Ave, Winona, MN 55987", "lat": 44.0370, "lng": -91.6720, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Faribault", "address": "200 S State Ave, Faribault, MN 55021", "lat": 44.2928, "lng": -93.2705, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Albert Lea", "address": "2510 Bridge Ave, Albert Lea, MN 56007", "lat": 43.6480, "lng": -93.3614, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Stillwater", "address": "1570 Frontage Rd W, Stillwater, MN 55082", "lat": 45.0542, "lng": -92.8611, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Chaska", "address": "120 Pioneer Trail, Chaska, MN 55318", "lat": 44.7893, "lng": -93.6020, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - Inver Grove Heights", "address": "5765 Cahill Ave, Inver Grove Heights, MN 55076", "lat": 44.8310, "lng": -93.0519, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Anytime Fitness - New Brighton", "address": "2700 N Snelling Ave, New Brighton, MN 55113", "lat": 45.0544, "lng": -93.1941, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},

    # ===================== PLANET FITNESS =====================
    {"name": "Planet Fitness - Bloomington", "address": "408 S Ave, Bloomington, MN 55425", "lat": 44.8557, "lng": -93.2422, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Brooklyn Park", "address": "7849 Brooklyn Blvd, Brooklyn Park, MN 55445", "lat": 45.0983, "lng": -93.3581, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Richfield", "address": "1612 E 66th St, Richfield, MN 55423", "lat": 44.8770, "lng": -93.2540, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Maplewood", "address": "3001 White Bear Ave N, Maplewood, MN 55109", "lat": 44.9862, "lng": -93.0170, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Minnetonka", "address": "13700 Wayzata Blvd, Minnetonka, MN 55305", "lat": 44.9693, "lng": -93.4688, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Woodbury", "address": "1845 Woodlane Dr, Woodbury, MN 55125", "lat": 44.9249, "lng": -92.9109, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Apple Valley", "address": "15050 Cedar Ave S, Apple Valley, MN 55124", "lat": 44.7302, "lng": -93.2177, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Rochester", "address": "1201 S Broadway, Rochester, MN 55904", "lat": 44.0103, "lng": -92.4650, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Duluth", "address": "1600 Miller Trunk Hwy, Duluth, MN 55811", "lat": 46.8188, "lng": -92.1412, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Coon Rapids", "address": "3430 124th Ave NW, Coon Rapids, MN 55433", "lat": 45.1410, "lng": -93.3532, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Fridley", "address": "250 57th Ave NE, Fridley, MN 55432", "lat": 45.0780, "lng": -93.2580, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Eagan", "address": "1276 Town Centre Dr, Eagan, MN 55123", "lat": 44.8089, "lng": -93.1675, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - St. Cloud", "address": "3333 W Division St, St. Cloud, MN 56301", "lat": 45.5470, "lng": -94.2100, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Mankato", "address": "1651 Madison Ave, Mankato, MN 56001", "lat": 44.1690, "lng": -93.9890, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},
    {"name": "Planet Fitness - Shakopee", "address": "8050 Old Carriage Court, Shakopee, MN 55379", "lat": 44.7710, "lng": -93.5190, "gym_type": "gym",
     "amenities": ["weights", "cardio", "tanning", "hydromassage"]},

    # ===================== YMCA / YWCA =====================
    {"name": "YWCA Uptown", "address": "2121 E Lake St, Minneapolis, MN 55407", "lat": 44.9488, "lng": -93.2467, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes", "track", "childcare"]},
    {"name": "YMCA Downtown Minneapolis", "address": "30 S 9th St, Minneapolis, MN 55402", "lat": 44.9764, "lng": -93.2735, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes", "track"]},
    {"name": "YMCA Midway", "address": "1761 University Ave W, St. Paul, MN 55104", "lat": 44.9555, "lng": -93.1720, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes", "childcare"]},
    {"name": "YMCA White Bear Lake", "address": "2100 Orchard Ln, White Bear Lake, MN 55110", "lat": 45.0662, "lng": -93.0197, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},
    {"name": "YMCA Southdale", "address": "7355 York Ave S, Edina, MN 55435", "lat": 44.8788, "lng": -93.3303, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes", "childcare"]},
    {"name": "YMCA Blaisdell", "address": "3335 Blaisdell Ave, Minneapolis, MN 55408", "lat": 44.9398, "lng": -93.2789, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},
    {"name": "YMCA Burnsville", "address": "200 W Burnsville Pkwy, Burnsville, MN 55337", "lat": 44.7672, "lng": -93.2784, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes", "childcare"]},
    {"name": "YMCA Elk River", "address": "711 Main St, Elk River, MN 55330", "lat": 45.3036, "lng": -93.5672, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},
    {"name": "YMCA Rochester", "address": "709 1st Ave SW, Rochester, MN 55902", "lat": 44.0191, "lng": -92.4741, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},
    {"name": "YMCA Eagan", "address": "550 Opperman Dr, Eagan, MN 55123", "lat": 44.7966, "lng": -93.1530, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes", "childcare"]},
    {"name": "YMCA Andover", "address": "15200 Hanson Blvd NW, Andover, MN 55304", "lat": 45.2520, "lng": -93.3367, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},
    {"name": "YMCA Hastings", "address": "300 11th St W, Hastings, MN 55033", "lat": 44.7436, "lng": -92.8585, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},
    {"name": "YMCA Ridgedale", "address": "12301 Ridgedale Dr, Minnetonka, MN 55305", "lat": 44.9694, "lng": -93.4580, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes", "childcare"]},
    {"name": "YMCA New Hope", "address": "7601 42nd Ave N, New Hope, MN 55427", "lat": 45.0378, "lng": -93.3861, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},
    {"name": "YMCA Emma B. Howe", "address": "8950 Springbrook Dr, Coon Rapids, MN 55433", "lat": 45.1360, "lng": -93.3210, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes", "childcare"]},
    {"name": "YMCA Duluth", "address": "302 W 1st St, Duluth, MN 55802", "lat": 46.7852, "lng": -92.1047, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},
    {"name": "YMCA St. Cloud", "address": "1530 Northway Dr, St. Cloud, MN 56303", "lat": 45.5560, "lng": -94.1802, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},

    # ===================== SNAP FITNESS =====================
    {"name": "Snap Fitness - St. Louis Park", "address": "5500 Excelsior Blvd, St. Louis Park, MN 55416", "lat": 44.9373, "lng": -93.3481, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Snap Fitness - Maple Grove", "address": "11298 Fountains Dr, Maple Grove, MN 55369", "lat": 45.1057, "lng": -93.4640, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Snap Fitness - Hastings", "address": "1170 Frontage Rd, Hastings, MN 55033", "lat": 44.7378, "lng": -92.8612, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Snap Fitness - Prior Lake", "address": "16389 Duluth Ave SE, Prior Lake, MN 55372", "lat": 44.7133, "lng": -93.4222, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Snap Fitness - Chanhassen", "address": "530 W 78th St, Chanhassen, MN 55317", "lat": 44.8612, "lng": -93.5308, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Snap Fitness - Waconia", "address": "985 Industrial Blvd, Waconia, MN 55387", "lat": 44.8509, "lng": -93.7910, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Snap Fitness - Northfield", "address": "1500 Clinton Ln, Northfield, MN 55057", "lat": 44.4653, "lng": -93.1700, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Snap Fitness - Monticello", "address": "220 W 7th St, Monticello, MN 55362", "lat": 45.3067, "lng": -93.7939, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Snap Fitness - Red Wing", "address": "213 Bush St, Red Wing, MN 55066", "lat": 44.5616, "lng": -92.5343, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},
    {"name": "Snap Fitness - Cambridge", "address": "140 Buchanan St S, Cambridge, MN 55008", "lat": 45.5728, "lng": -93.2244, "gym_type": "gym",
     "amenities": ["weights", "cardio", "24/7 access"]},

    # ===================== COREPOWER YOGA =====================
    {"name": "CorePower Yoga - Uptown", "address": "3003 Lyndale Ave S, Minneapolis, MN 55408", "lat": 44.9484, "lng": -93.2882, "gym_type": "gym",
     "amenities": ["yoga", "heated classes", "sculpt"]},
    {"name": "CorePower Yoga - North Loop", "address": "212 N 2nd St, Minneapolis, MN 55401", "lat": 44.9849, "lng": -93.2710, "gym_type": "gym",
     "amenities": ["yoga", "heated classes", "sculpt"]},
    {"name": "CorePower Yoga - Edina", "address": "3943 W 50th St, Edina, MN 55424", "lat": 44.9132, "lng": -93.3346, "gym_type": "gym",
     "amenities": ["yoga", "heated classes", "sculpt"]},
    {"name": "CorePower Yoga - St. Paul", "address": "867 Grand Ave, St. Paul, MN 55105", "lat": 44.9400, "lng": -93.1263, "gym_type": "gym",
     "amenities": ["yoga", "heated classes", "sculpt"]},
    {"name": "CorePower Yoga - Woodbury", "address": "9040 Hudson Rd, Woodbury, MN 55125", "lat": 44.9175, "lng": -92.9070, "gym_type": "gym",
     "amenities": ["yoga", "heated classes", "sculpt"]},
    {"name": "CorePower Yoga - Maple Grove", "address": "7880 Main St N, Maple Grove, MN 55369", "lat": 45.0845, "lng": -93.4450, "gym_type": "gym",
     "amenities": ["yoga", "heated classes", "sculpt"]},

    # ===================== ORANGETHEORY FITNESS =====================
    {"name": "Orangetheory - Edina", "address": "3916 W 50th St, Edina, MN 55424", "lat": 44.9130, "lng": -93.3334, "gym_type": "gym",
     "amenities": ["HIIT", "heart rate monitoring", "classes"]},
    {"name": "Orangetheory - Minnetonka", "address": "11209 Highway 7, Minnetonka, MN 55305", "lat": 44.9384, "lng": -93.4691, "gym_type": "gym",
     "amenities": ["HIIT", "heart rate monitoring", "classes"]},
    {"name": "Orangetheory - Woodbury", "address": "9060 Hudson Rd, Woodbury, MN 55125", "lat": 44.9172, "lng": -92.9066, "gym_type": "gym",
     "amenities": ["HIIT", "heart rate monitoring", "classes"]},
    {"name": "Orangetheory - Maple Grove", "address": "7876 Main St N, Maple Grove, MN 55369", "lat": 45.0843, "lng": -93.4447, "gym_type": "gym",
     "amenities": ["HIIT", "heart rate monitoring", "classes"]},
    {"name": "Orangetheory - Eagan", "address": "1280 Town Centre Dr, Eagan, MN 55123", "lat": 44.8090, "lng": -93.1680, "gym_type": "gym",
     "amenities": ["HIIT", "heart rate monitoring", "classes"]},
    {"name": "Orangetheory - St. Paul", "address": "860 Grand Ave, St. Paul, MN 55105", "lat": 44.9398, "lng": -93.1260, "gym_type": "gym",
     "amenities": ["HIIT", "heart rate monitoring", "classes"]},

    # ===================== CROSSFIT =====================
    {"name": "CrossFit Minneapolis", "address": "411 Main St NE, Minneapolis, MN 55413", "lat": 44.9936, "lng": -93.2578, "gym_type": "gym",
     "amenities": ["crossfit", "weightlifting", "classes", "open gym"]},
    {"name": "CrossFit St. Paul", "address": "671 Vandalia St, St. Paul, MN 55114", "lat": 44.9651, "lng": -93.1955, "gym_type": "gym",
     "amenities": ["crossfit", "weightlifting", "classes", "open gym"]},
    {"name": "CrossFit Edina", "address": "5000 W 36th St, St. Louis Park, MN 55416", "lat": 44.9322, "lng": -93.3450, "gym_type": "gym",
     "amenities": ["crossfit", "weightlifting", "classes"]},
    {"name": "CrossFit Lino Lakes", "address": "7580 Village Dr, Lino Lakes, MN 55014", "lat": 45.1530, "lng": -93.0966, "gym_type": "gym",
     "amenities": ["crossfit", "weightlifting", "classes", "open gym"]},
    {"name": "CrossFit Woodbury", "address": "2060 Eagle Creek Ln, Woodbury, MN 55129", "lat": 44.8985, "lng": -92.8920, "gym_type": "gym",
     "amenities": ["crossfit", "weightlifting", "classes"]},
    {"name": "CrossFit Burnsville", "address": "14225 Ewing Ave S, Burnsville, MN 55306", "lat": 44.7565, "lng": -93.3050, "gym_type": "gym",
     "amenities": ["crossfit", "weightlifting", "classes"]},

    # ===================== UNIVERSITY / COLLEGE =====================
    {"name": "U of M Recreation Center", "address": "1906 University Ave SE, Minneapolis, MN 55455", "lat": 44.9738, "lng": -93.2322, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "rock climbing", "track"]},
    {"name": "St. Thomas Recreation Center", "address": "2115 Summit Ave, St. Paul, MN 55105", "lat": 44.9400, "lng": -93.1912, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "track"]},
    {"name": "Macalester College Fitness Center", "address": "1600 Grand Ave, St. Paul, MN 55105", "lat": 44.9381, "lng": -93.1695, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball"]},
    {"name": "Augsburg University Si Melby Hall", "address": "2211 Riverside Ave, Minneapolis, MN 55454", "lat": 44.9695, "lng": -93.2400, "gym_type": "both",
     "amenities": ["weights", "cardio", "basketball", "track"]},
    {"name": "UMD Sports & Health Center", "address": "1216 Ordean Ct, Duluth, MN 55812", "lat": 46.8194, "lng": -92.0852, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "rock climbing"]},
    {"name": "MSU Mankato Myers Field House", "address": "213 Stadium Rd, Mankato, MN 56001", "lat": 44.1450, "lng": -93.9985, "gym_type": "both",
     "amenities": ["weights", "cardio", "pool", "basketball", "track"]},

    # ===================== LA FITNESS =====================
    {"name": "LA Fitness - Bloomington", "address": "7901 Southtown Center, Bloomington, MN 55431", "lat": 44.8589, "lng": -93.3078, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},
    {"name": "LA Fitness - Brooklyn Center", "address": "5929 Earle Brown Dr, Brooklyn Center, MN 55430", "lat": 45.0665, "lng": -93.3305, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},
    {"name": "LA Fitness - Roseville", "address": "2100 Snelling Ave N, Roseville, MN 55113", "lat": 45.0100, "lng": -93.1670, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "basketball", "classes"]},

    # ===================== CRUNCH / EOS / FLAGSHIP / THE FIRM =====================
    {"name": "Crunch Fitness - Roseville", "address": "2480 Fairview Ave N, Roseville, MN 55113", "lat": 45.0141, "lng": -93.1684, "gym_type": "gym",
     "amenities": ["weights", "cardio", "classes", "tanning"]},
    {"name": "Crunch Fitness - Burnsville", "address": "14300 Burnhaven Dr, Burnsville, MN 55306", "lat": 44.7540, "lng": -93.2860, "gym_type": "gym",
     "amenities": ["weights", "cardio", "classes", "tanning"]},
    {"name": "EoS Fitness - Coon Rapids", "address": "12995 Riverdale Dr NW, Coon Rapids, MN 55448", "lat": 45.1612, "lng": -93.3122, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "classes", "tanning"]},
    {"name": "EoS Fitness - Blaine", "address": "10950 Baltimore St NE, Blaine, MN 55449", "lat": 45.1560, "lng": -93.2060, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "classes", "tanning"]},
    {"name": "Flagship Athletic Club - Eden Prairie", "address": "755 Prairie Center Dr, Eden Prairie, MN 55344", "lat": 44.8543, "lng": -93.4596, "gym_type": "gym",
     "amenities": ["weights", "cardio", "pool", "classes", "childcare"]},
    {"name": "The Firm", "address": "1101 LaSalle Ave, Minneapolis, MN 55403", "lat": 44.9720, "lng": -93.2772, "gym_type": "gym",
     "amenities": ["weights", "cardio", "classes", "sauna"]},

    # ===================== F45 / BURN BOOT CAMP / BOUTIQUE =====================
    {"name": "F45 Training - North Loop", "address": "400 N 1st Ave, Minneapolis, MN 55401", "lat": 44.9860, "lng": -93.2720, "gym_type": "gym",
     "amenities": ["HIIT", "classes", "circuit training"]},
    {"name": "F45 Training - Edina", "address": "6801 York Ave S, Edina, MN 55435", "lat": 44.8850, "lng": -93.3310, "gym_type": "gym",
     "amenities": ["HIIT", "classes", "circuit training"]},
    {"name": "Burn Boot Camp - Plymouth", "address": "4155 Vinewood Ln N, Plymouth, MN 55442", "lat": 45.0300, "lng": -93.4150, "gym_type": "gym",
     "amenities": ["bootcamp", "classes", "childcare"]},
    {"name": "Burn Boot Camp - Woodbury", "address": "1750 Weir Dr, Woodbury, MN 55125", "lat": 44.9200, "lng": -92.9200, "gym_type": "gym",
     "amenities": ["bootcamp", "classes", "childcare"]},
    {"name": "barre3 - Uptown Minneapolis", "address": "3020 Hennepin Ave, Minneapolis, MN 55408", "lat": 44.9520, "lng": -93.2980, "gym_type": "gym",
     "amenities": ["barre", "yoga", "classes"]},
    {"name": "Alchemy 365 - North Loop", "address": "729 N Washington Ave, Minneapolis, MN 55401", "lat": 44.9880, "lng": -93.2730, "gym_type": "gym",
     "amenities": ["HIIT", "yoga", "strength", "classes"]},
    {"name": "Alchemy 365 - Edina", "address": "5009 France Ave S, Edina, MN 55410", "lat": 44.9110, "lng": -93.3290, "gym_type": "gym",
     "amenities": ["HIIT", "yoga", "strength", "classes"]},
    {"name": "9Round - Lakeville", "address": "20710 Holyoke Ave, Lakeville, MN 55044", "lat": 44.6500, "lng": -93.2420, "gym_type": "gym",
     "amenities": ["kickboxing", "circuit training", "classes"]},
    {"name": "Title Boxing Club - Eagan", "address": "1280 Town Centre Dr, Eagan, MN 55123", "lat": 44.8088, "lng": -93.1677, "gym_type": "gym",
     "amenities": ["boxing", "kickboxing", "classes"]},

    # ===================== INDEPENDENT / LOCAL =====================
    {"name": "The Movement Minneapolis", "address": "3118 Grimes Ave N, Robbinsdale, MN 55422", "lat": 45.0231, "lng": -93.3391, "gym_type": "gym",
     "amenities": ["powerlifting", "strongman", "open gym"]},
    {"name": "Sweat Social", "address": "4022 E Lake St, Minneapolis, MN 55406", "lat": 44.9487, "lng": -93.2210, "gym_type": "gym",
     "amenities": ["classes", "yoga", "HIIT", "community"]},
    {"name": "Minneapolis Bouldering Project", "address": "1433 NE Quincy St, Minneapolis, MN 55413", "lat": 44.9950, "lng": -93.2470, "gym_type": "gym",
     "amenities": ["rock climbing", "bouldering", "yoga", "weights"]},
    {"name": "Vertical Endeavors - St. Paul", "address": "845 Phalen Blvd, St. Paul, MN 55106", "lat": 44.9670, "lng": -93.0610, "gym_type": "gym",
     "amenities": ["rock climbing", "bouldering", "classes"]},
    {"name": "Vertical Endeavors - Bloomington", "address": "2540 Nicollet Ave, Minneapolis, MN 55404", "lat": 44.9590, "lng": -93.2780, "gym_type": "gym",
     "amenities": ["rock climbing", "bouldering", "classes"]},
    {"name": "Midwest Mountaineering Climbing Gym", "address": "309 Cedar Ave S, Minneapolis, MN 55454", "lat": 44.9725, "lng": -93.2478, "gym_type": "gym",
     "amenities": ["rock climbing", "outdoor gear", "classes"]},
    {"name": "Uppercut Boxing Gym", "address": "3944 Nicollet Ave, Minneapolis, MN 55409", "lat": 44.9250, "lng": -93.2780, "gym_type": "gym",
     "amenities": ["boxing", "kickboxing", "classes"]},
    {"name": "Luce Line Fitness", "address": "500 Elm St, Watertown, MN 55388", "lat": 44.9635, "lng": -93.8475, "gym_type": "gym",
     "amenities": ["weights", "cardio", "classes"]},

    # ======================================================
    # MINNESOTA BASKETBALL COURTS
    # ======================================================

    # --- Minneapolis Parks ---
    {"name": "Peavey Park", "address": "730 E 22nd St, Minneapolis, MN 55404", "lat": 44.9587, "lng": -93.2588, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "playground"]},
    {"name": "The Commons", "address": "425 Portland Ave S, Minneapolis, MN 55415", "lat": 44.9748, "lng": -93.2617, "gym_type": "basketball_court",
     "amenities": ["outdoor court", "downtown"]},
    {"name": "Elliot Park", "address": "1000 E 14th St, Minneapolis, MN 55404", "lat": 44.9663, "lng": -93.2587, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "playground"]},
    {"name": "Powderhorn Park", "address": "3400 15th Ave S, Minneapolis, MN 55407", "lat": 44.9370, "lng": -93.2599, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "lake nearby"]},
    {"name": "North Commons Park", "address": "1801 James Ave N, Minneapolis, MN 55411", "lat": 44.9983, "lng": -93.2980, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "indoor gym", "lights", "pool nearby"]},
    {"name": "Rev. Dr. Martin Luther King Jr. Park", "address": "4055 Nicollet Ave S, Minneapolis, MN 55409", "lat": 44.9240, "lng": -93.2782, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "community center"]},
    {"name": "Matthews Park", "address": "2318 29th Ave S, Minneapolis, MN 55406", "lat": 44.9507, "lng": -93.2316, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "rec center"]},
    {"name": "Harrison Park", "address": "503 Irving Ave N, Minneapolis, MN 55405", "lat": 44.9817, "lng": -93.2947, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "playground"]},
    {"name": "Loring Park", "address": "1382 Willow St, Minneapolis, MN 55403", "lat": 44.9692, "lng": -93.2828, "gym_type": "basketball_court",
     "amenities": ["outdoor court", "downtown", "lake nearby"]},
    {"name": "Folwell Park", "address": "1615 Dowling Ave N, Minneapolis, MN 55412", "lat": 45.0219, "lng": -93.2969, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "rec center", "playground"]},
    {"name": "Bottineau Park", "address": "2000 NE 2nd St, Minneapolis, MN 55418", "lat": 44.9978, "lng": -93.2466, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "rec center"]},
    {"name": "Van Cleve Park", "address": "901 15th Ave SE, Minneapolis, MN 55414", "lat": 44.9801, "lng": -93.2299, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "near U of M"]},
    {"name": "Whittier Park", "address": "425 W 26th St, Minneapolis, MN 55405", "lat": 44.9560, "lng": -93.2843, "gym_type": "basketball_court",
     "amenities": ["outdoor court", "playground"]},
    {"name": "Hiawatha Park", "address": "4305 E 43rd St, Minneapolis, MN 55406", "lat": 44.9219, "lng": -93.2211, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "playground"]},
    {"name": "Luxton Park", "address": "116 Williams Ave SE, Minneapolis, MN 55414", "lat": 44.9790, "lng": -93.2280, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "rec center"]},
    {"name": "Armatage Park", "address": "2500 W 57th St, Minneapolis, MN 55410", "lat": 44.9050, "lng": -93.3130, "gym_type": "basketball_court",
     "amenities": ["outdoor court", "playground"]},
    {"name": "Corcoran Park", "address": "3334 20th Ave S, Minneapolis, MN 55407", "lat": 44.9390, "lng": -93.2460, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights"]},
    {"name": "Keewaydin Park", "address": "3030 E 53rd St, Minneapolis, MN 55417", "lat": 44.9110, "lng": -93.2270, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "rec center", "playground"]},
    {"name": "Logan Park", "address": "690 13th Ave NE, Minneapolis, MN 55413", "lat": 44.9930, "lng": -93.2560, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights"]},
    {"name": "Waite Park", "address": "1810 NE 34th Ave, Minneapolis, MN 55418", "lat": 45.0060, "lng": -93.2300, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "rec center"]},
    {"name": "Webber Park", "address": "4400 Dupont Ave N, Minneapolis, MN 55412", "lat": 45.0290, "lng": -93.2960, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "pool nearby", "playground"]},
    {"name": "Phillips Park", "address": "2323 11th Ave S, Minneapolis, MN 55404", "lat": 44.9570, "lng": -93.2620, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "community center"]},
    {"name": "Sibley Park", "address": "1900 E 40th St, Minneapolis, MN 55407", "lat": 44.9250, "lng": -93.2400, "gym_type": "basketball_court",
     "amenities": ["outdoor courts"]},
    {"name": "Northeast Park", "address": "1530 Johnson St NE, Minneapolis, MN 55413", "lat": 44.9980, "lng": -93.2510, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights"]},

    # --- St. Paul Parks ---
    {"name": "Como Park", "address": "1360 Lexington Pkwy N, St. Paul, MN 55103", "lat": 44.9791, "lng": -93.1483, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lake nearby", "playground"]},
    {"name": "Mears Park", "address": "221 E 5th St, St. Paul, MN 55101", "lat": 44.9488, "lng": -93.0856, "gym_type": "basketball_court",
     "amenities": ["outdoor court", "downtown"]},
    {"name": "MLK Park - St. Paul", "address": "270 N Kent St, St. Paul, MN 55102", "lat": 44.9502, "lng": -93.1173, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "playground"]},
    {"name": "Phalen Park", "address": "1600 Phalen Dr, St. Paul, MN 55106", "lat": 44.9852, "lng": -93.0372, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lake nearby", "playground"]},
    {"name": "Dunning Park", "address": "1221 Dunning Field, St. Paul, MN 55117", "lat": 44.9916, "lng": -93.1136, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "rec center"]},
    {"name": "Central Village Park", "address": "433 N Western Ave, St. Paul, MN 55103", "lat": 44.9622, "lng": -93.1297, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "playground"]},
    {"name": "Rice Park", "address": "109 W 4th St, St. Paul, MN 55102", "lat": 44.9447, "lng": -93.0960, "gym_type": "basketball_court",
     "amenities": ["outdoor court", "downtown"]},
    {"name": "Battle Creek Park", "address": "2401 Upper Afton Rd, St. Paul, MN 55119", "lat": 44.9380, "lng": -93.0190, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "trails", "playground"]},
    {"name": "Highland Park", "address": "1200 Montreal Ave, St. Paul, MN 55116", "lat": 44.9210, "lng": -93.1690, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "pool nearby", "rec center"]},
    {"name": "Hazel Park", "address": "1663 Maryland Ave E, St. Paul, MN 55106", "lat": 44.9700, "lng": -93.0490, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "rec center"]},

    # --- Suburban Courts ---
    {"name": "Bloomington Athletic Center Courts", "address": "4600 W 98th St, Bloomington, MN 55437", "lat": 44.8394, "lng": -93.3351, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights"]},
    {"name": "Plymouth Creek Center Courts", "address": "14800 34th Ave N, Plymouth, MN 55447", "lat": 45.0418, "lng": -93.4726, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "playground"]},
    {"name": "Valley Park - Apple Valley", "address": "14600 Hayes Rd, Apple Valley, MN 55124", "lat": 44.7329, "lng": -93.2361, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "playground"]},
    {"name": "Central Park - Eagan", "address": "1501 Central Pkwy, Eagan, MN 55121", "lat": 44.8140, "lng": -93.1638, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "playground"]},
    {"name": "Maple Grove Central Park", "address": "12951 Weaver Lake Rd, Maple Grove, MN 55369", "lat": 45.1023, "lng": -93.4575, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "playground"]},
    {"name": "Lakeville Heritage Center Courts", "address": "20110 Holyoke Ave, Lakeville, MN 55044", "lat": 44.6510, "lng": -93.2430, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "indoor gym"]},
    {"name": "Eden Prairie Community Center Courts", "address": "16700 Valley View Rd, Eden Prairie, MN 55346", "lat": 44.8450, "lng": -93.4530, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "indoor gym", "lights"]},
    {"name": "Burnsville Civic Center Courts", "address": "100 Civic Center Pkwy, Burnsville, MN 55337", "lat": 44.7670, "lng": -93.2790, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights"]},
    {"name": "Woodbury Central Park Courts", "address": "8595 Central Park Pl, Woodbury, MN 55125", "lat": 44.9160, "lng": -92.9230, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "playground"]},
    {"name": "Brooklyn Park Palmer Lake Courts", "address": "7110 Palmer Lake Dr, Brooklyn Park, MN 55443", "lat": 45.1120, "lng": -93.3760, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "lake nearby"]},
    {"name": "Roseville Cedarholm Community Courts", "address": "2323 Hamline Ave N, Roseville, MN 55113", "lat": 45.0150, "lng": -93.1870, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "playground"]},
    {"name": "Richfield Veterans Park Courts", "address": "6335 Portland Ave, Richfield, MN 55423", "lat": 44.8780, "lng": -93.2660, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights"]},
    {"name": "Shakopee Lions Park Courts", "address": "1101 Adams St S, Shakopee, MN 55379", "lat": 44.7730, "lng": -93.5170, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "playground"]},
    {"name": "Rochester Silver Lake Park Courts", "address": "840 7th St NE, Rochester, MN 55906", "lat": 44.0290, "lng": -92.4570, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lake nearby"]},
    {"name": "Duluth Lincoln Park Courts", "address": "2525 W 3rd St, Duluth, MN 55806", "lat": 46.7670, "lng": -92.1290, "gym_type": "basketball_court",
     "amenities": ["outdoor courts"]},
    {"name": "St. Cloud Whitney Park Courts", "address": "1700 Stearns County Rd, St. Cloud, MN 56303", "lat": 45.5510, "lng": -94.1720, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "playground"]},
    {"name": "Mankato Tourtellotte Park Courts", "address": "Tourtellotte Park, Mankato, MN 56001", "lat": 44.1620, "lng": -93.9990, "gym_type": "basketball_court",
     "amenities": ["outdoor courts"]},
    {"name": "Cottage Grove Kingston Park Courts", "address": "8170 Keats Ave S, Cottage Grove, MN 55016", "lat": 44.8260, "lng": -92.9130, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "playground"]},
    {"name": "Inver Grove Heights Hilltop Park Courts", "address": "8085 Cahill Ave, Inver Grove Heights, MN 55076", "lat": 44.8300, "lng": -93.0520, "gym_type": "basketball_court",
     "amenities": ["outdoor courts"]},
    {"name": "Coon Rapids Brickyard Park Courts", "address": "10301 Hanson Blvd NW, Coon Rapids, MN 55433", "lat": 45.1350, "lng": -93.3380, "gym_type": "basketball_court",
     "amenities": ["outdoor courts", "lights", "playground"]},
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
    print(f"Created {len(gym_ids)} real Minnesota gyms and courts.")

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
