"""Sensor platform for Synthetic Home."""

import logging
from typing import Any

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
from .model import ParsedHome, ParsedEntity, filter_attributes
from .entity import SyntheticEntity

_LOGGER = logging.getLogger(__name__)


SUPPORTED_ATTRIBUTES = set(
    {
        "device_class",
        "state_class",
        "native_value",
        "native_unit_of_measurement",
    }
)


def map_attributes(entity: ParsedEntity) -> dict[str, Any]:
    """Convert attributes from home assistant exports to the class here."""
    result = {}
    for k, v in entity.attributes.items():
        if k == "unit_of_measurement":
            k = "native_unit_of_measurement"
        elif k == "native_value":
            k = "native_value"
        result[k] = v
    entity.attributes = result
    return filter_attributes(entity, SUPPORTED_ATTRIBUTES)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up sensor platform."""

    synthetic_home: ParsedHome = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        SyntheticHomeSensor(
            entity, state=entity.state, **map_attributes(entity)
        )
        for entity in synthetic_home.entities
        if entity.platform == SENSOR_DOMAIN
    )


class SyntheticHomeSensor(SyntheticEntity, SensorEntity):
    """synthetic_home Sensor class."""

    def __init__(
        self,
        entity: ParsedEntity,
        state: StateType | None = None,
        *,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_value: StateType | None = None,
        native_unit_of_measurement: str | None = None
    ) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(entity)
        if device_class:
            self._attr_device_class = device_class
        if state_class:
            self._attr_state_class = state_class
        if native_value or state:
            self._attr_native_value = native_value or state
        if native_unit_of_measurement:
            self._attr_native_unit_of_measurement = native_unit_of_measurement
