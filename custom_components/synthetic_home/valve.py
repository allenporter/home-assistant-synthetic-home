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
        state: str | None = None
    ) -> None:
        """Initialize the SyntheticValve."""
        super().__init__(device, key)
        if supported_features is not None:
            self._attr_supported_features = ValveEntityFeature(0) | supported_features
        if state:
            self._attr_is_closed = state == "closed"

    async def async_open_valve(self) -> None:
        """Open the valve."""
        self._attr_is_closed = False
        self.async_write_ha_state()

    async def async_close_valve(self) -> None:
        """Close valve."""
        self._attr_is_closed = True
        self.async_write_ha_state()
