"""Binary sensor platform for Synthetic Home."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
    DOMAIN as BINARY_SENSOR_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .model import ParsedDevice
from .entity import SyntheticDeviceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up binary_sensor platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]
    for device in synthetic_home.devices:
        for entity in device.entities:
            _LOGGER.debug(entity)

    async_add_devices(
        SyntheticHomeBinarySensor(device, entity.entity_key, **entity.attributes)
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == BINARY_SENSOR_DOMAIN
    )


class SyntheticHomeBinarySensor(SyntheticDeviceEntity, BinarySensorEntity):
    """synthetic_home binary_sensor class."""

    def __init__(
        self,
        device: ParsedDevice,
        key: str,
        device_class: BinarySensorDeviceClass | None = None,
        state: bool = False,
    ) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(device, key)
        if key not in device.friendly_name.lower():  # Avoid "Motion Motion"
            self._attr_name = key.capitalize()
        self._attr_device_class = device_class
        self._attr_is_on = state
