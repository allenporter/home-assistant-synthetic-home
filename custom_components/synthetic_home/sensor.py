"""Sensor platform for Synthetic Home."""

import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
    StateType,
    DOMAIN as SENSOR_DOMAIN,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .model import ParsedHome, ParsedDevice
from .entity import SyntheticDeviceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up sensor platform."""

    synthetic_home: ParsedHome = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        SyntheticHomeSensor(device, entity.entity_key, **entity.attributes)
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == SENSOR_DOMAIN
    )


class SyntheticHomeSensor(SyntheticDeviceEntity, SensorEntity):
    """synthetic_home Sensor class."""

    def __init__(
        self,
        device: ParsedDevice,
        key: str,
        *,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_value: StateType | None = None,
        state: StateType | None = None,
        native_unit_of_measurement: str | None = None
    ) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(device, key)
        self._attr_name = key.capitalize()
        if device_class:
            self._attr_device_class = device_class
        if state_class:
            self._attr_state_class = state_class
        if native_value or state:
            self._attr_native_value = native_value or state
        if native_unit_of_measurement:
            self._attr_native_unit_of_measurement = native_unit_of_measurement
