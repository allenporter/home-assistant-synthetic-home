"""Valve platform for Synthetic Home."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.valve import (
    ValveEntity,
    ValveEntityFeature,
    DOMAIN as VALVE_DOMAIN,
)

from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticDeviceEntity
from .model import ParsedDevice


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up valve platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticValve(device, entity.entity_key, **entity.attributes)
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == VALVE_DOMAIN
    )


class SyntheticValve(SyntheticDeviceEntity, ValveEntity):
    """synthetic_home valve class."""

    _attr_reports_position = False

    def __init__(
        self,
        device: ParsedDevice,
        key: str,
        *,
        supported_features: ValveEntityFeature | None = None,
        state: str | None = None,
        current_valve_position: int | None = None,
        is_closed: bool | None = None,
        is_closing: bool | None = None,
        is_opening: bool | None = None,
        reports_position: bool | None = None,
    ) -> None:
        """Initialize the SyntheticValve."""
        super().__init__(device, key)
        if supported_features is not None:
            self._attr_supported_features = ValveEntityFeature(0) | supported_features
        if state:
            self._attr_is_closed = state == "closed"
        if current_valve_position is not None:
            self._attr_current_valve_position = current_valve_position
        if is_closed is not None:
            self._attr_is_closed = is_closed
        if is_closing is not None:
            self._attr_is_closing = is_closing
        if reports_position is not None:
            self._attr_reports_position = reports_position

    async def async_open_valve(self) -> None:
        """Open the valve."""
        self._attr_is_closed = False
        self.async_write_ha_state()

    async def async_close_valve(self) -> None:
        """Close valve."""
        self._attr_is_closed = True
        self.async_write_ha_state()

    async def async_set_valve_position(self, position: int) -> None:
        """Move the valve to a specific position."""
        self._attr_current_valve_position = position
        self._attr_is_closed = self._attr_current_valve_position == 0
        self.async_write_ha_state()

    async def async_stop_valve(self) -> None:
        """Stop the valve."""
        self._attr_is_closing = False
        self._attr_is_opening = False
        self.async_write_ha_state()
