"""Light platform for Synthetic Home."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
    ATTR_RGBW_COLOR,
    LightEntityDescription,
    DOMAIN as LIGHT_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticDeviceEntity
from .model import ParsedDevice

_LOGGER = logging.getLogger(__name__)

class SyntheticLightEntityDescription(LightEntityDescription, frozen_or_thawed=True):
    """Entity description for a light."""

    supported_color_modes: set[ColorMode] | None = (None,)
    color_mode: ColorMode | None = (None,)
    brightness: int | None = (None,)
    rgbw_color: tuple[int, int, int, int] | None = (None,)


LIGHTS: tuple[LightEntityDescription, ...] = (
    SyntheticLightEntityDescription(
        key="light-dimmable",
        supported_color_modes={ColorMode.BRIGHTNESS},
        color_mode=ColorMode.BRIGHTNESS,
    ),
    SyntheticLightEntityDescription(
        key="light",
        supported_color_modes={ColorMode.ONOFF},
        color_mode=ColorMode.ONOFF,
    ),
    SyntheticLightEntityDescription(
        key="light-rgbw",
        supported_color_modes={ColorMode.RGBW},
        color_mode=ColorMode.RGBW,
    ),
)
LIGHT_MAP = {desc.key: desc for desc in LIGHTS}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up light platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeLight(device, LIGHT_MAP[entity.entity_key], **entity.attributes)
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == LIGHT_DOMAIN
    )


class SyntheticHomeLight(SyntheticDeviceEntity, LightEntity):
    """synthetic_home light class."""

    def __init__(
        self,
        device: ParsedDevice,
        entity_desc: SyntheticLightEntityDescription,
        *,
        state: str | None = None,
        brightness: int | None = None,
        rgbw_color: tuple[int, int, int, int] | None = None,
    ) -> None:
        """Initialize the device."""
        super().__init__(device, entity_desc.key)
        _LOGGER.debug("state=%s", state)
        self.entity_description = entity_desc
        self._attr_supported_color_modes = entity_desc.supported_color_modes
        if state is not None:
            self._attr_state = state
        elif brightness is not None and brightness > 0:
            self._attr_state = "on"
        self._attr_color_mode = entity_desc.color_mode
        self._attr_brightness = brightness
        self._attr_rgbw_color = rgbw_color

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the light."""
        if brightness := kwargs.get(ATTR_BRIGHTNESS):
            self._attr_brightness = brightness
        if rgbw_color := kwargs.get(ATTR_RGBW_COLOR):
            self._attr_rgbw_color = rgbw_color
        self._attr_state = "on"
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the light."""
        self._attr_state = "off"
        self.async_write_ha_state()

    @property
    def is_on(self):
        """Return true if the light is on."""
        return self._attr_state == "on"
