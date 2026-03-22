"""
Wearable provider registry.
Add new providers here — they become available automatically
without modifying any route or service code.
"""

from app.services.wearables.base import WearableProvider
from app.services.wearables.fitbit import FitbitProvider
from app.services.wearables.apple_health import AppleHealthProvider
from app.services.wearables.samsung_health import SamsungHealthProvider

# Register all providers
_providers: dict[str, WearableProvider] = {}


def _register_defaults():
    for cls in [FitbitProvider, AppleHealthProvider, SamsungHealthProvider]:
        provider = cls()
        _providers[provider.provider_name] = provider


_register_defaults()


def get_provider(name: str) -> WearableProvider | None:
    return _providers.get(name)


def list_providers() -> list[str]:
    return list(_providers.keys())


def register_provider(provider: WearableProvider):
    """Register a new wearable provider at runtime."""
    _providers[provider.provider_name] = provider
