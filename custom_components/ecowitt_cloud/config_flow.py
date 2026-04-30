"""Config flow for Ecowitt Cloud integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    API_DEVICE_LIST,
    API_TIMEOUT,
    CONF_API_KEY,
    CONF_APPLICATION_KEY,
    CONF_GATEWAY_NAME,
    CONF_MAC,
    CONF_MODE,
    CONF_POLL_INTERVAL,
    CONF_PORT,
    DEFAULT_MODE,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_PORT,
    DOMAIN,
    MODE_AUTO,
    MODE_CLOUD,
    MODE_LOCAL,
    MODES,
)

_LOGGER = logging.getLogger(__name__)


async def _fetch_device_list(
    session: aiohttp.ClientSession,
    application_key: str,
    api_key: str,
) -> list[dict]:
    """Fetch list of gateways from Ecowitt API."""
    params = {
        "application_key": application_key,
        "api_key": api_key,
    }
    try:
        async with session.get(
            API_DEVICE_LIST,
            params=params,
            timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
        ) as response:
            if response.status != 200:
                return []
            result = await response.json()
            if result.get("code") != 0:
                return []
            return result.get("data", {}).get("list", [])
    except aiohttp.ClientError:
        return []


class EcowittCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ecowitt Cloud."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._application_key: str = ""
        self._api_key: str = ""
        self._gateways: list[dict] = []
        self._selected_gateways: list[dict] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Step 1: Enter API credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._application_key = user_input[CONF_APPLICATION_KEY]
            self._api_key = user_input[CONF_API_KEY]

            session = async_get_clientsession(self.hass)
            self._gateways = await _fetch_device_list(
                session, self._application_key, self._api_key
            )

            if not self._gateways:
                errors["base"] = "cannot_connect"
            else:
                return await self.async_step_select_gateways()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_APPLICATION_KEY): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    async def async_step_select_gateways(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Step 2: Select which gateways to add."""
        errors: dict[str, str] = {}

        gateway_options = {
            gw["mac"]: f"{gw.get('name', gw['mac'])} ({gw['mac']})"
            for gw in self._gateways
        }

        if user_input is not None:
            selected_macs = user_input.get("selected_macs", [])
            if not selected_macs:
                errors["base"] = "no_gateway_selected"
            else:
                self._selected_gateways = [
                    gw for gw in self._gateways if gw["mac"] in selected_macs
                ]
                return await self.async_step_mode()

        return self.async_show_form(
            step_id="select_gateways",
            data_schema=vol.Schema(
                {
                    vol.Required("selected_macs"): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                {"value": mac, "label": label}
                                for mac, label in gateway_options.items()
                            ],
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
            errors=errors,
        )

    async def async_step_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Step 3: Select data mode and options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            mode = user_input[CONF_MODE]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            poll_interval = user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

            # Create one config entry per selected gateway
            entries_created = 0
            for gateway in self._selected_gateways:
                await self.async_set_unique_id(
                    f"{DOMAIN}_{gateway['mac'].replace(':', '').replace('-', '')}"
                )
                self._abort_if_unique_id_configured()

                self.hass.async_create_task(
                    self.hass.config_entries.flow.async_init(
                        DOMAIN,
                        context={"source": "import"},
                        data={
                            CONF_APPLICATION_KEY: self._application_key,
                            CONF_API_KEY: self._api_key,
                            CONF_MAC: gateway["mac"],
                            CONF_GATEWAY_NAME: gateway.get("name", gateway["mac"]),
                            CONF_MODE: mode,
                            CONF_PORT: port,
                            CONF_POLL_INTERVAL: poll_interval,
                        },
                    )
                ) if entries_created > 0 else None
                entries_created += 1

            # Create first entry directly
            first_gw = self._selected_gateways[0]
            return self.async_create_entry(
                title=first_gw.get("name", first_gw["mac"]),
                data={
                    CONF_APPLICATION_KEY: self._application_key,
                    CONF_API_KEY: self._api_key,
                    CONF_MAC: first_gw["mac"],
                    CONF_GATEWAY_NAME: first_gw.get("name", first_gw["mac"]),
                    CONF_MODE: mode,
                    CONF_PORT: port,
                    CONF_POLL_INTERVAL: poll_interval,
                },
            )

        return self.async_show_form(
            step_id="mode",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODE, default=DEFAULT_MODE): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                {"value": MODE_CLOUD, "label": "Cloud only (polling)"},
                                {"value": MODE_LOCAL, "label": "Local only (push from gateway)"},
                                {"value": MODE_AUTO, "label": "Auto (Local priority + Cloud fallback)"},
                            ],
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): NumberSelector(
                        NumberSelectorConfig(
                            min=1024,
                            max=65535,
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=5,
                            max=60,
                            step=5,
                            unit_of_measurement="min",
                            mode=NumberSelectorMode.SLIDER,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> EcowittCloudOptionsFlow:
        """Get options flow."""
        return EcowittCloudOptionsFlow(config_entry)


class EcowittCloudOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Ecowitt Cloud."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_mode = self.config_entry.data.get(CONF_MODE, DEFAULT_MODE)
        current_port = self.config_entry.data.get(CONF_PORT, DEFAULT_PORT)
        current_interval = self.config_entry.data.get(
            CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODE, default=current_mode): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                {"value": MODE_CLOUD, "label": "Cloud only"},
                                {"value": MODE_LOCAL, "label": "Local only"},
                                {"value": MODE_AUTO, "label": "Auto (Local + Cloud fallback)"},
                            ],
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(CONF_PORT, default=current_port): NumberSelector(
                        NumberSelectorConfig(
                            min=1024,
                            max=65535,
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_POLL_INTERVAL, default=current_interval
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=5,
                            max=60,
                            step=5,
                            unit_of_measurement="min",
                            mode=NumberSelectorMode.SLIDER,
                        )
                    ),
                }
            ),
        )
