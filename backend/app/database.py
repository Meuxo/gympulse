from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings
import certifi
import ssl

settings = get_settings()

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    """Connect to MongoDB and set up indexes."""
    global client, db

    # Build connection kwargs for Atlas SSL compatibility
    kwargs = {}
    if "mongodb+srv" in settings.MONGODB_URL or "mongodb.net" in settings.MONGODB_URL:
        kwargs["tls"] = True
        kwargs["tlsCAFile"] = certifi.where()
        kwargs["tlsAllowInvalidCertificates"] = False
        # Fallback: if certifi doesn't work, allow invalid certs
        try:
            test_client = AsyncIOMotorClient(
                settings.MONGODB_URL, tls=True, tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000,
            )
            await test_client.admin.command("ping")
            test_client.close()
        except Exception:
            kwargs["tlsAllowInvalidCertificates"] = True
            kwargs.pop("tlsCAFile", None)

    client = AsyncIOMotorClient(settings.MONGODB_URL, **kwargs)
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
