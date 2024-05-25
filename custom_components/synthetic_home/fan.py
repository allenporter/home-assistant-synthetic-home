"""Fan platform for Synthetic Home."""

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
from .entity import SyntheticDeviceEntity
from .model import ParsedDevice


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up fan platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticFan(device, entity.entity_key, **entity.attributes)
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == FAN_DOMAIN
    )


class SyntheticFan(SyntheticDeviceEntity, FanEntity):
    """synthetic_home fan class."""

    _attr_reports_position = False

    def __init__(
        self,
        device: ParsedDevice,
        key: str,
        *,
        supported_features: FanEntityFeature | None = None,
        state: str | None = None,
        is_on: bool | None = None,
        oscillating: bool | None = None,
    ) -> None:
        """Initialize the SyntheticFan."""
        super().__init__(device, key)
        if supported_features is not None:
            self._attr_supported_features = FanEntityFeature(0) | supported_features
        if state:
            self._attr_percentage = 100 if (state == "on") else 0
        if is_on is not None:
            self._attr_percentage = 100 if is_on else 0
        if oscillating is not None:
            self._attr_oscillating = oscillating

    async def async_turn_on(
        self,
        speed: str | None = None,
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
