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
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    API_DEVICE_LIST,
    API_TIMEOUT,
    CONF_API_KEY,
    CONF_APPLICATION_KEY,
    CONF_GATEWAY_NAME,
    CONF_MAC,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
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
                return await self.async_step_options()

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

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Step 3: Polling interval."""
        if user_input is not None:
            poll_interval = user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

            first_gw = self._selected_gateways[0]
            first_mac_clean = first_gw["mac"].replace(":", "").replace("-", "")
            await self.async_set_unique_id(f"{DOMAIN}_{first_mac_clean}")
            self._abort_if_unique_id_configured()

            # Schedule additional gateways via import flow
            for gw in self._selected_gateways[1:]:
                self.hass.async_create_task(
                    self.hass.config_entries.flow.async_init(
                        DOMAIN,
                        context={"source": "import"},
                        data={
                            CONF_APPLICATION_KEY: self._application_key,
                            CONF_API_KEY: self._api_key,
                            CONF_MAC: gw["mac"],
                            CONF_GATEWAY_NAME: gw.get("name", gw["mac"]),
                            CONF_POLL_INTERVAL: poll_interval,
                        },
                    )
                )

            return self.async_create_entry(
                title=first_gw.get("name", first_gw["mac"]),
                data={
                    CONF_APPLICATION_KEY: self._application_key,
                    CONF_API_KEY: self._api_key,
                    CONF_MAC: first_gw["mac"],
                    CONF_GATEWAY_NAME: first_gw.get("name", first_gw["mac"]),
                    CONF_POLL_INTERVAL: poll_interval,
                },
            )

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema(
                {
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
        )

    async def async_step_import(
        self, user_input: dict[str, Any]
    ) -> config_entries.FlowResult:
        """Handle programmatic creation of additional gateways."""
        mac_clean = user_input[CONF_MAC].replace(":", "").replace("-", "")
        await self.async_set_unique_id(f"{DOMAIN}_{mac_clean}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=user_input.get(CONF_GATEWAY_NAME, user_input[CONF_MAC]),
            data=user_input,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> EcowittCloudOptionsFlow:
        """Get options flow."""
        return EcowittCloudOptionsFlow()


class EcowittCloudOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Ecowitt Cloud."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.data.get(
            CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
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
