"""Switch platform for Synthetic Home."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.switch import (
    SwitchEntity,
    SwitchDeviceClass,
    DOMAIN as SWITCH_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes


SUPPORTED_ATTRIBUTES = set(
    {
        "device_class",
        "is_on",
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up switch platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeBinarySwitch(
            entity,
            state=entity.state,
            **filter_attributes(entity, SUPPORTED_ATTRIBUTES),
        )
        for entity in synthetic_home.entities
        if entity.platform == SWITCH_DOMAIN
    )


class SyntheticHomeBinarySwitch(SyntheticEntity, SwitchEntity):
    """synthetic_home switch class."""

    def __init__(
        self,
        entity: ParsedEntity,
        state: str | None = None,
        *,
        is_on: bool | None = None,
        device_class: SwitchDeviceClass | None = None,
    ) -> None:
        """Initialize SyntheticHomeBinarySwitch."""
        super().__init__(entity)
        if state is not None:
            self._attr_is_on = state == "on"
        if is_on is not None:
            self._attr_is_on = is_on
        if device_class is not None:
            self._attr_device_class = device_class

    async def async_turn_on(
        self, **kwargs: Any
    ) -> None:  # pylint: disable=unused-argument
        """Turn on the switch."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(
        self, **kwargs: Any
    ) -> None:  # pylint: disable=unused-argument
        """Turn off the switch."""
        self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        return self._attr_is_on
