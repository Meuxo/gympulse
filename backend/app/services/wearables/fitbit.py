"""
Fitbit wearable integration.
Implements the WearableProvider interface for Fitbit API.
Requires FITBIT_CLIENT_ID and FITBIT_CLIENT_SECRET in environment.
"""

from typing import Optional
from datetime import datetime
import httpx
from app.services.wearables.base import WearableProvider as BaseProvider
from app.config import get_settings


class FitbitProvider(BaseProvider):

    @property
    def provider_name(self) -> str:
        return "fitbit"

    async def authorize(self, user_id: str) -> dict:
        settings = get_settings()
        if not settings.FITBIT_CLIENT_ID:
            return {
                "status": "not_configured",
                "message": "Set FITBIT_CLIENT_ID and FITBIT_CLIENT_SECRET env vars.",
            }
        auth_url = (
            f"https://www.fitbit.com/oauth2/authorize?"
            f"response_type=code&client_id={settings.FITBIT_CLIENT_ID}"
            f"&redirect_uri={settings.FITBIT_REDIRECT_URI}"
            f"&scope=activity+heartrate+sleep+profile"
        )
        return {"status": "redirect", "authorization_url": auth_url}

    async def handle_callback(self, code: str, user_id: str) -> dict:
        settings = get_settings()
        # Exchange authorization code for tokens
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.fitbit.com/oauth2/token",
                data={
                    "client_id": settings.FITBIT_CLIENT_ID,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.FITBIT_REDIRECT_URI,
                    "code": code,
                },
                auth=(settings.FITBIT_CLIENT_ID, settings.FITBIT_CLIENT_SECRET),
            )
        if response.status_code != 200:
            return {"status": "error", "message": "Failed to exchange code for tokens"}

        tokens = response.json()
        return {
            "status": "connected",
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "expires_in": tokens.get("expires_in"),
        }

    async def sync_data(
        self,
        user_id: str,
        access_token: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[dict]:
        """Fetch activity data from Fitbit API."""
        if not access_token:
            return []

        date_str = (date_to or datetime.utcnow()).strftime("%Y-%m-%d")
        headers = {"Authorization": f"Bearer {access_token}"}
        records = []

        async with httpx.AsyncClient() as client:
            # Fetch daily activity summary
            resp = await client.get(
                f"https://api.fitbit.com/1/user/-/activities/date/{date_str}.json",
                headers=headers,
            )
            if resp.status_code == 200:
                data = resp.json().get("summary", {})
                if "steps" in data:
                    records.append({
                        "provider": "fitbit",
                        "metric_type": "steps",
                        "value": data["steps"],
                        "unit": "steps",
                        "recorded_at": date_str,
                    })
                if "caloriesOut" in data:
                    records.append({
                        "provider": "fitbit",
                        "metric_type": "calories_burned",
                        "value": data["caloriesOut"],
                        "unit": "kcal",
                        "recorded_at": date_str,
                    })
                if "activeMinutes" in data or "fairlyActiveMinutes" in data:
                    active = data.get("fairlyActiveMinutes", 0) + data.get("veryActiveMinutes", 0)
                    records.append({
                        "provider": "fitbit",
                        "metric_type": "active_minutes",
                        "value": active,
                        "unit": "minutes",
                        "recorded_at": date_str,
                    })

        return records

    async def refresh_token(self, refresh_token: str) -> dict:
        settings = get_settings()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.fitbit.com/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                auth=(settings.FITBIT_CLIENT_ID, settings.FITBIT_CLIENT_SECRET),
            )
        if response.status_code != 200:
            return {"status": "error", "message": "Failed to refresh token"}

        tokens = response.json()
        return {
            "status": "refreshed",
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
        }
