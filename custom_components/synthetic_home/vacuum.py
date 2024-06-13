"""Vacuum platform for Synthetic Home."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,
    STATE_CLEANING,
    STATE_RETURNING,
    DOMAIN as VACUUM_DOMAIN,
)
from homeassistant.const import STATE_OFF, STATE_PAUSED

from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes


SUPPORTED_ATTRIBUTES = set(
    {
        "supported_features",
        "fan_speed",
        "fan_speed_list",
        "battery_icon",
        "battery_level",
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up vacuum platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticVacuum(
            entity,
            state=entity.state,
            **filter_attributes(entity, SUPPORTED_ATTRIBUTES),
        )
        for entity in synthetic_home.entities
        if entity.platform == VACUUM_DOMAIN
    )


class SyntheticVacuum(SyntheticEntity, StateVacuumEntity):
    """synthetic_home vacuum class."""

    def __init__(
        self,
        entity: ParsedEntity,
        state: str | None = None,
        *,
        supported_features: VacuumEntityFeature | None = None,
        fan_speed: str | None = None,
        fan_speed_list: list[str] | None = None,
        battery_icon: str | None = None,
        battery_level: int | None = None,
    ) -> None:
        """Initialize the SyntheticVacuum."""
        super().__init__(entity)
        if supported_features is not None:
            self._attr_supported_features = VacuumEntityFeature(0) | supported_features
        if state:
            self._attr_state = state
        if fan_speed is not None:
            self._attr_fan_speed = fan_speed
        if fan_speed_list is not None:
            self._attr_fan_speed_list = fan_speed_list
        if battery_icon is not None:
            self._attr_battery_icon = battery_icon
        if battery_level is not None:
            self._attr_battery_level = battery_level

    async def async_stop(self, **kwargs: Any) -> None:
        """Stop the vacuum cleaner.

        This method must be run in the event loop.
        """
        self._attr_state = STATE_OFF
        self.async_write_ha_state()

    async def async_return_to_base(self, **kwargs: Any) -> None:
        """Set the vacuum cleaner to return to the dock.

        This method must be run in the event loop.
        """
        self._attr_state = STATE_RETURNING
        self.async_write_ha_state()

    async def async_clean_spot(self, **kwargs: Any) -> None:
        """Perform a spot clean-up."""
        self._attr_state = STATE_CLEANING
        self.async_write_ha_state()

    async def async_start(self) -> None:
        """Start or resume the cleaning task.

        This method must be run in the event loop.
        """
        self._attr_state = STATE_CLEANING
        self.async_write_ha_state()

    async def async_pause(self) -> None:
        """Pause the cleaning task.

        This method must be run in the event loop.
        """
        self._attr_state = STATE_PAUSED
        self.async_write_ha_state()

    async def async_set_fan_speed(self, fan_speed: str, **kwargs: Any) -> None:
        """Set fan speed."""
        self._attr_fan_speed = fan_speed
        self.async_write_ha_state()

    async def async_send_command(
        self,
        command: str,
        params: dict[str, Any] | list[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Send a command to a vacuum cleaner."""
        pass

    async def async_locate(self, **kwargs: Any) -> None:
        """Locate the vacuum cleaner."""
        pass
