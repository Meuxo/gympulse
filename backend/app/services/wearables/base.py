"""
Base wearable provider interface.
All wearable integrations implement this interface so new providers
can be added without modifying existing code.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime


class WearableProvider(ABC):
    """Abstract base class for wearable device integrations."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier (e.g., 'fitbit', 'apple_health')."""
        ...

    @abstractmethod
    async def authorize(self, user_id: str) -> dict:
        """
        Start the OAuth flow or return authorization instructions.
        Returns a dict with authorization URL or instructions.
        """
        ...

    @abstractmethod
    async def handle_callback(self, code: str, user_id: str) -> dict:
        """
        Handle the OAuth callback after user authorization.
        Returns tokens or connection status.
        """
        ...

    @abstractmethod
    async def sync_data(
        self,
        user_id: str,
        access_token: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[dict]:
        """
        Fetch data from the wearable API and return normalized records.
        Each record should match the WearableSyncCreate schema.
        """
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh an expired access token.
        Returns new access_token and optionally new refresh_token.
        """
        ...
