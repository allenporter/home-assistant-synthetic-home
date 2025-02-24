"""Device tracker platform for Synthetic Home."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.device_tracker import (
    TrackerEntity,
    DOMAIN as DEVICE_TRACKER_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes

_LOGGER = logging.getLogger(__name__)

SUPPORTED_ATTRIBUTES = set(
    {
        "location_name",
        "lattiude",
        "longitude",
        "location_accuracy",
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up device_tracker platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeTrackerEntity(
            entity,
            state=entity.state,
            **filter_attributes(entity, SUPPORTED_ATTRIBUTES),
        )
        for entity in synthetic_home.entities
        if entity.platform == DEVICE_TRACKER_DOMAIN
    )


class SyntheticHomeTrackerEntity(SyntheticEntity, TrackerEntity):
    """synthetic_home tracker entity class."""

    def __init__(
        self,
        entity: ParsedEntity,
        state: str | None = None,
        *,
        location_name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        location_accuracy: int | None = None,
    ) -> None:
        """Initialize SyntheticHomeBinarySwitch."""
        super().__init__(entity)
        if state is not None:
            self._attr_location_name = state
        if location_name is not None:
            self._attr_location_name = location_name
        if latitude is not None:
            self._attr_latitude = latitude
        if longitude is not None:
            self._attr_longitude = longitude
        if location_accuracy is not None:
            self._attr_location_accuracy = location_accuracy
