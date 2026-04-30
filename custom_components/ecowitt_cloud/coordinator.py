"""Data coordinator for Ecowitt Cloud integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_DEVICE_REAL_TIME,
    API_TIMEOUT,
    ALL_CALLBACKS,
    CONF_API_KEY,
    CONF_APPLICATION_KEY,
    CONF_MAC,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    PRESSURE_UNIT_HPA,
    RAINFALL_UNIT_MM,
    SOLAR_UNIT_WM2,
    TEMP_UNIT_CELSIUS,
    WIND_UNIT_KMH,
)

_LOGGER = logging.getLogger(__name__)


class EcowittCloudCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for Ecowitt Cloud API polling."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        config: dict[str, Any],
    ) -> None:
        """Initialize the coordinator."""
        self._session = session
        self._application_key = config[CONF_APPLICATION_KEY]
        self._api_key = config[CONF_API_KEY]
        self._mac = config[CONF_MAC]
        poll_interval = config.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self._mac}",
            update_interval=timedelta(minutes=poll_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Ecowitt Cloud API."""
        params = {
            "application_key": self._application_key,
            "api_key": self._api_key,
            "mac": self._mac,
            "call_back": ",".join(ALL_CALLBACKS),
            "temp_unitid": TEMP_UNIT_CELSIUS,
            "pressure_unitid": PRESSURE_UNIT_HPA,
            "wind_speed_unitid": WIND_UNIT_KMH,
            "rainfall_unitid": RAINFALL_UNIT_MM,
            "solar_irradiance_unitid": SOLAR_UNIT_WM2,
        }

        try:
            async with self._session.get(
                API_DEVICE_REAL_TIME,
                params=params,
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as response:
                if response.status == 401:
                    raise ConfigEntryAuthFailed("Invalid API credentials")
                if response.status != 200:
                    raise UpdateFailed(
                        f"API returned HTTP {response.status}"
                    )

                result = await response.json()

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Network error: {err}") from err

        code = result.get("code")
        if code == -1:
            raise ConfigEntryAuthFailed("Invalid application_key or api_key")
        if code != 0:
            raise UpdateFailed(
                f"API error code {code}: {result.get('msg', 'Unknown error')}"
            )

        data = result.get("data", {})
        _LOGGER.debug("Ecowitt Cloud data received for %s: %s", self._mac, data)
        return data
