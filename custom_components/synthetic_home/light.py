"""Light platform for Synthetic Home."""

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
    ATTR_RGBW_COLOR,
    DOMAIN as LIGHT_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes

_LOGGER = logging.getLogger(__name__)

SUPPORTED_ATTRIBUTES = set(
    {
        "supported_color_modes",
        "color_mode",
        "brightness",
        "rgbw_color",
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up light platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeLight(
            entity,
            state=entity.state,
            **filter_attributes(entity.attributes, SUPPORTED_ATTRIBUTES),
        )
        for entity in synthetic_home.entities
        if entity.platform == LIGHT_DOMAIN
    )


class SyntheticHomeLight(SyntheticEntity, LightEntity):
    """synthetic_home light class."""

    def __init__(
        self,
        entity: ParsedEntity,
        state: str | None = None,
        supported_color_modes: set[ColorMode] | None = None,
        color_mode: ColorMode | None = None,
        *,
        brightness: int | None = None,
        rgbw_color: tuple[int, int, int, int] | None = None,
    ) -> None:
        """Initialize the device."""
        super().__init__(entity)
        self._attr_supported_color_modes = supported_color_modes
        self._attr_is_on = state is not None and state == "on"
        if brightness is not None and brightness > 0:
            self._attr_is_on = True
        self._attr_color_mode = color_mode
        self._attr_brightness = brightness
        self._attr_rgbw_color = rgbw_color

    async def async_turn_on(
        self, **kwargs: Any
    ) -> None:  # pylint: disable=unused-argument
        """Turn on the light."""
        if brightness := kwargs.get(ATTR_BRIGHTNESS):
            self._attr_brightness = brightness
        if rgbw_color := kwargs.get(ATTR_RGBW_COLOR):
            self._attr_rgbw_color = rgbw_color
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(
        self, **kwargs: Any
    ) -> None:  # pylint: disable=unused-argument
        """Turn off the light."""
        self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return true if the light is on."""
        return self._attr_is_on
