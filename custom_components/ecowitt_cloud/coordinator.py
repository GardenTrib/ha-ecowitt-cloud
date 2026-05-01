"""Data coordinator for Ecowitt Cloud integration."""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ALL_CALLBACKS,
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
        # Mutable set — invalid callbacks are removed at runtime
        self._callbacks: set[str] = set(ALL_CALLBACKS)
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
        """Perform API request, silently removing unsupported callbacks (code 40016)."""
        while True:
            if not self._callbacks:
                _LOGGER.error("%s: no valid callbacks remaining", self._mac)
                return {}

            params = {
                "application_key": self._application_key,
                "api_key": self._api_key,
                "mac": self._mac,
                "call_back": ",".join(sorted(self._callbacks)),
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

            if code == 40016:
                # A requested callback is not supported by this gateway.
                # Parse the callback name from the message and remove it.
                msg = result.get("msg", "")
                match = re.match(r"^(\S+)\s+is\s+invalid", msg, re.IGNORECASE)
                invalid_cb = match.group(1) if match else None

                if invalid_cb and invalid_cb in self._callbacks:
                    self._callbacks.discard(invalid_cb)
                    _LOGGER.info(
                        "%s: callback '%s' not supported by this gateway — removed",
                        self._mac,
                        invalid_cb,
                    )
                    continue  # retry immediately with reduced callback list
                else:
                    raise UpdateFailed(
                        f"{self._mac}: API error code 40016 — {msg}"
                    )

            if code != 0:
                raise UpdateFailed(
                    f"{self._mac}: API error code {code} — {result.get('msg', 'unknown')}"
                )

            data = result.get("data", {})
            _LOGGER.debug("%s: data updated (%d callbacks)", self._mac, len(data))

            # Log battery fields to help discover field names
            batt_fields = {
                f"{cb}.{field}": val
                for cb, cb_data in data.items()
                if isinstance(cb_data, dict)
                for field, val in cb_data.items()
                if "batt" in field.lower()
            }
            if batt_fields:
                _LOGGER.debug("%s: battery fields found: %s", self._mac, batt_fields)
            else:
                _LOGGER.debug("%s: no battery fields found in response", self._mac)

            return data
