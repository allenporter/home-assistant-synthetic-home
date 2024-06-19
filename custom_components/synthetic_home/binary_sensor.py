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
from .model import ParsedEntity, filter_attributes
from .entity import SyntheticEntity

_LOGGER = logging.getLogger(__name__)


SUPPORTED_ATTRIBUTES = {"device_class"}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up binary_sensor platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeBinarySensor(
            entity,
            state=entity.state,
            **filter_attributes(entity, SUPPORTED_ATTRIBUTES),
        )
        for entity in synthetic_home.entities
        if entity.platform == BINARY_SENSOR_DOMAIN
    )


class SyntheticHomeBinarySensor(SyntheticEntity, BinarySensorEntity):
    """synthetic_home binary_sensor class."""

    def __init__(
        self,
        entity: ParsedEntity,
        *,
        device_class: BinarySensorDeviceClass | None = None,
        state: bool | None = None,
    ) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(entity)
        if device_class is not None:
            self._attr_device_class = device_class
        self._attr_is_on = state if state is not None else False
