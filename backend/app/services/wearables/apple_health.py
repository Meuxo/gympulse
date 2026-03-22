"""
Apple Health integration.
Apple Health data must be synced from an iOS device via HealthKit.
This provider handles receiving data pushed from the mobile app.
"""

from typing import Optional
from datetime import datetime
from app.services.wearables.base import WearableProvider as BaseProvider


class AppleHealthProvider(BaseProvider):

    @property
    def provider_name(self) -> str:
        return "apple_health"

    async def authorize(self, user_id: str) -> dict:
        return {
            "status": "device_required",
            "message": "Apple Health requires iOS device authorization via HealthKit.",
            "instructions": [
                "1. Open the FitTrack app on your iPhone",
                "2. Go to Settings > Connected Devices",
                "3. Tap 'Connect Apple Health'",
                "4. Grant access to the requested health data categories",
                "5. Data will sync automatically",
            ],
        }

    async def handle_callback(self, code: str, user_id: str) -> dict:
        # Apple Health doesn't use OAuth — data is pushed from the device
        return {
            "status": "not_applicable",
            "message": "Apple Health uses device-level HealthKit authorization, not OAuth.",
        }

    async def sync_data(
        self,
        user_id: str,
        access_token: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[dict]:
        # Data is pushed from the iOS app, not pulled from an API.
        # This method would process incoming data from the mobile app.
        return []

    async def refresh_token(self, refresh_token: str) -> dict:
        return {"status": "not_applicable", "message": "Apple Health does not use tokens."}
