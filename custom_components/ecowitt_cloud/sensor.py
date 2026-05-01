"""Sensor platform for Ecowitt Cloud integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
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
    SENSOR_DESCRIPTIONS,
)

from .coordinator import EcowittCloudCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ecowitt Cloud sensors."""
    coordinator: EcowittCloudCoordinator = hass.data[DOMAIN][entry.entry_id]
    mac = entry.data[CONF_MAC]
    gateway_name = entry.data.get(CONF_GATEWAY_NAME, mac)

    entities: list[EcowittSensor] = []
    data = coordinator.data or {}

    for (callback_key, field_key), description in SENSOR_DESCRIPTIONS.items():
        callback_data = data.get(callback_key, {})
        if callback_data and field_key in callback_data:
            entities.append(
                EcowittSensor(
                    coordinator=coordinator,
                    mac=mac,
                    gateway_name=gateway_name,
                    callback_key=callback_key,
                    field_key=field_key,
                    description=description,
                )
            )

    _LOGGER.debug(
        "Setting up %d Ecowitt sensors for gateway %s", len(entities), mac
    )
    async_add_entities(entities)


class EcowittSensor(CoordinatorEntity[EcowittCloudCoordinator], SensorEntity):
    """Representation of an Ecowitt sensor."""

    def __init__(
        self,
        coordinator: EcowittCloudCoordinator,
        mac: str,
        gateway_name: str,
        callback_key: str,
        field_key: str,
        description: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._mac = mac
        self._gateway_name = gateway_name
        self._callback_key = callback_key
        self._field_key = field_key
        self._description = description

        mac_clean = mac.replace(":", "").replace("-", "")
        self._attr_unique_id = f"{mac_clean}_{callback_key}_{field_key}"
        self._attr_name = description["name"]
        self._attr_icon = description.get("icon")

        if description.get("device_class"):
            self._attr_device_class = SensorDeviceClass(description["device_class"])

        if description.get("state_class"):
            self._attr_state_class = SensorStateClass(description["state_class"])

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac_clean)},
            name=gateway_name,
            manufacturer="Ecowitt",
            model="GW Series Gateway",
        )

    @property
    def native_value(self) -> float | str | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        field_data = self._get_field_data()
        value = field_data.get("value")
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return value

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit from the API response."""
        if self.coordinator.data is None:
            return None
        return self._get_field_data().get("unit")

    def _get_field_data(self) -> dict[str, Any]:
        """Return the raw field dict from coordinator data."""
        callback_data = self.coordinator.data.get(self._callback_key, {})
        return callback_data.get(self._field_key, {})
