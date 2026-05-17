"""Binary sensor platform for Ecowitt Cloud integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_GATEWAY_NAME,
    CONF_MAC,
    DOMAIN,
    WFC01_BINARY_FIELDS,
)
from .coordinator import EcowittCloudCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ecowitt Cloud binary sensors."""
    coordinator: EcowittCloudCoordinator = hass.data[DOMAIN][entry.entry_id]
    mac = entry.data[CONF_MAC]
    gateway_name = entry.data.get(CONF_GATEWAY_NAME, mac)

    entities: list[EcowittBinarySensor] = []
    data = coordinator.data or {}

    # WFC01 WittFlow valve binary sensors (dynamic callback key = "WFC01-{serial}")
    for key, cb_data in data.items():
        if key.startswith("WFC01-") and isinstance(cb_data, dict):
            for field_key, description in WFC01_BINARY_FIELDS.items():
                if field_key in cb_data:
                    entities.append(
                        EcowittBinarySensor(
                            coordinator=coordinator,
                            mac=mac,
                            gateway_name=gateway_name,
                            callback_key=key,
                            field_key=field_key,
                            description=description,
                        )
                    )

    _LOGGER.debug(
        "Setting up %d Ecowitt binary sensors for gateway %s",
        len(entities),
        mac,
    )
    async_add_entities(entities)


class EcowittBinarySensor(
    CoordinatorEntity[EcowittCloudCoordinator], BinarySensorEntity
):
    """Representation of an Ecowitt binary sensor (valve open/closed)."""

    def __init__(
        self,
        coordinator: EcowittCloudCoordinator,
        mac: str,
        gateway_name: str,
        callback_key: str,
        field_key: str,
        description: dict[str, Any],
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._mac = mac
        self._gateway_name = gateway_name
        self._callback_key = callback_key
        self._field_key = field_key
        self._description = description

        mac_clean = mac.replace(":", "").replace("-", "")
        self._attr_unique_id = f"{mac_clean}_{callback_key}_{field_key}"
        self._attr_name = description["name"]
        self._attr_device_class = BinarySensorDeviceClass(description["device_class"])

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac_clean)},
            name=gateway_name,
            manufacturer="Ecowitt",
            model="GW Series Gateway",
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if valve is open."""
        if self.coordinator.data is None:
            return None
        callback_data = self.coordinator.data.get(self._callback_key, {})
        field_data = callback_data.get(self._field_key, {})
        value = field_data.get("value")
        if value is None:
            return None
        return str(value) == "1"

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        if self.is_on:
            return self._description["icon_on"]
        return self._description["icon_off"]
