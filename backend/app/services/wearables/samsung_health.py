"""
Samsung Health integration.
Samsung Health SDK requires partner access.
This is a placeholder that follows the same interface.
"""

from typing import Optional
from datetime import datetime
from app.services.wearables.base import WearableProvider as BaseProvider
from app.config import get_settings


class SamsungHealthProvider(BaseProvider):

    @property
    def provider_name(self) -> str:
        return "samsung_health"

    async def authorize(self, user_id: str) -> dict:
        settings = get_settings()
        if not settings.SAMSUNG_HEALTH_CLIENT_ID:
            return {
                "status": "not_configured",
                "message": "Set SAMSUNG_HEALTH_CLIENT_ID and SAMSUNG_HEALTH_CLIENT_SECRET env vars.",
            }
        # Samsung Health uses its own SDK flow
        return {
            "status": "device_required",
            "message": "Samsung Health requires Galaxy device authorization.",
            "instructions": [
                "1. Open FitTrack on your Galaxy device",
                "2. Go to Settings > Connected Devices",
                "3. Tap 'Connect Samsung Health'",
                "4. Grant access in Samsung Health app",
            ],
        }

    async def handle_callback(self, code: str, user_id: str) -> dict:
        return {
            "status": "placeholder",
            "message": "Samsung Health OAuth callback — implement with Samsung Partner SDK.",
        }

    async def sync_data(
        self,
        user_id: str,
        access_token: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[dict]:
        # Placeholder — would use Samsung Health SDK to fetch data
        return []

    async def refresh_token(self, refresh_token: str) -> dict:
        return {"status": "placeholder", "message": "Implement with Samsung Partner SDK."}
