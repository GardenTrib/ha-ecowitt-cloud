"""Data coordinator for Ecowitt Cloud integration."""
from __future__ import annotations

import asyncio
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
    CONF_API_KEY,
    CONF_APPLICATION_KEY,
    CONF_MAC,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

_RETRY_ATTEMPTS = 3
_RETRY_BASE_DELAY = 5  # seconds; doubled each attempt (5s, 10s)


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
        """Fetch data from Ecowitt Cloud API with retry on transient errors."""
        last_err: UpdateFailed | None = None

        for attempt in range(_RETRY_ATTEMPTS):
            try:
                return await self._fetch()
            except ConfigEntryAuthFailed:
                raise
            except UpdateFailed as err:
                last_err = err
                if attempt < _RETRY_ATTEMPTS - 1:
                    delay = _RETRY_BASE_DELAY * (2 ** attempt)
                    _LOGGER.warning(
                        "%s: fetch failed (attempt %d/%d), retrying in %ds: %s",
                        self._mac,
                        attempt + 1,
                        _RETRY_ATTEMPTS,
                        delay,
                        err,
                    )
                    await asyncio.sleep(delay)

        raise last_err  # type: ignore[misc]

    async def _fetch(self) -> dict[str, Any]:
        """Perform API request using call_back=all to discover all available sensors."""
        params = {
            "application_key": self._application_key,
            "api_key": self._api_key,
            "mac": self._mac,
            "call_back": "all",
        }

        try:
            async with self._session.get(
                API_DEVICE_REAL_TIME,
                params=params,
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as response:
                if response.status == 401:
                    raise ConfigEntryAuthFailed(
                        f"{self._mac}: invalid API credentials (HTTP 401)"
                    )
                if response.status != 200:
                    raise UpdateFailed(
                        f"{self._mac}: API returned HTTP {response.status}"
                    )
                result = await response.json()

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"{self._mac}: network error — {err}") from err

        code = result.get("code")

        if code == -1:
            raise ConfigEntryAuthFailed(
                f"{self._mac}: invalid application_key or api_key (code -1)"
            )

        if code != 0:
            raise UpdateFailed(
                f"{self._mac}: API error code {code} — {result.get('msg', 'unknown')}"
            )

        data = result.get("data", {})
        _LOGGER.debug("%s: data updated (%d top-level keys)", self._mac, len(data))
        return data
