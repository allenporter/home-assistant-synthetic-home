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
from .entity import SyntheticDeviceEntity
from .model import ParsedDevice


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up vacuum platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticVacuum(device, entity.entity_key, **entity.attributes)
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == VACUUM_DOMAIN
    )


class SyntheticVacuum(SyntheticDeviceEntity, StateVacuumEntity):
    """synthetic_home vacuum class."""

    def __init__(
        self,
        device: ParsedDevice,
        key: str,
        *,
        supported_features: VacuumEntityFeature | None = None,
        state: str | None = None
    ) -> None:
        """Initialize the SyntheticVacuum."""
        super().__init__(device, key)
        if supported_features is not None:
            self._attr_supported_features = VacuumEntityFeature(0) | supported_features
        if state:
            self._attr_state = state

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
