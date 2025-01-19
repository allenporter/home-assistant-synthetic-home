"""Fan platform for Synthetic Home."""

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature,
    DOMAIN as FAN_DOMAIN,
)

from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes

_LOGGER = logging.getLogger(__name__)

SUPPORTED_ATTRIBUTES = set(
    {
        "supported_features",
        "device_class",
        "is_on",
        "oscillating",
        "current_direction",
        "percentage",
        "preset_mode",
        "preset_modes",
        "speed_count",
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up fan platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticFan(
            entity,
            state=entity.state,
            **filter_attributes(entity, SUPPORTED_ATTRIBUTES),
        )
        for entity in synthetic_home.entities
        if entity.platform == FAN_DOMAIN
    )


class SyntheticFan(SyntheticEntity, FanEntity):
    """synthetic_home fan class."""

    _attr_reports_position = False

    def __init__(
        self,
        entity: ParsedEntity,
        state: str | None,
        *,
        supported_features: FanEntityFeature | None = None,
        is_on: bool | None = None,
        oscillating: bool | None = None,
        current_direction: str | None = None,
        percentage: int | None = None,
        preset_mode: str | None = None,
        preset_modes: list[str] | None = None,
        speed_count: int | None = None,
    ) -> None:
        """Initialize the SyntheticFan."""
        super().__init__(entity)
        if supported_features is not None:
            self._attr_supported_features = (
                FanEntityFeature(0)
                | FanEntityFeature.TURN_ON
                | FanEntityFeature.TURN_OFF
                | supported_features
            )
        if state is not None:
            self._attr_percentage = 100 if (state == "on") else 0
        elif is_on is not None:
            self._attr_percentage = 100 if is_on else 0
        if percentage is not None:
            self._attr_percentage = percentage
        if oscillating is not None:
            self._attr_oscillating = oscillating
        if current_direction is not None:
            self._attr_current_direction = current_direction
        if preset_mode is not None:
            self._attr_preset_mode = preset_mode
        if preset_modes is not None:
            self._preset_modes = preset_modes
        if speed_count is not None:
            self._attr_speed_count = speed_count
        _LOGGER.debug("self._attr_percentage=%s", self._attr_percentage)

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        self._attr_current_direction = direction
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        self._attr_preset_mode = preset_mode
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        self._attr_percentage = percentage
        self.async_write_ha_state()

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        self._attr_percentage = 100
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        self._attr_percentage = 0
        self.async_write_ha_state()

    async def async_oscillate(self, oscillating: bool) -> None:
        """Oscillate the fan."""
        self._attr_oscillating = oscillating
        self.async_write_ha_state()
