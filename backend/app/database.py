from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings
import ssl
import certifi

settings = get_settings()

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    """Connect to MongoDB and set up indexes."""
    global client, db

    url = settings.MONGODB_URL
    kwargs = {}

    # For Atlas connections, configure SSL properly
    if "mongodb+srv" in url or "mongodb.net" in url:
        # Create permissive SSL context for compatibility with Atlas
        ctx = ssl.create_default_context(cafile=certifi.where())
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        # Lower security level to allow more cipher suites (fixes Python 3.13 + OpenSSL 3.x)
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        kwargs["tls"] = True
        kwargs["tlsAllowInvalidCertificates"] = True

    client = AsyncIOMotorClient(url, **kwargs)
    db = client[settings.MONGODB_DB_NAME]

    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.workouts.create_index([("user_id", 1), ("date", -1)])
    await db.wearable_syncs.create_index([("user_id", 1), ("provider", 1), ("synced_at", -1)])
    await db.gyms.create_index([("location", "2dsphere")])
    await db.gyms.create_index("name")
    await db.crowd_reports.create_index([("gym_id", 1), ("timestamp", -1)])
    await db.basketball_reports.create_index([("gym_id", 1), ("timestamp", -1)])

    print("Connected to MongoDB")


async def close_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


def get_db():
    return db
