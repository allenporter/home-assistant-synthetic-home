"""Switch platform for Synthetic Home."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity, DOMAIN as LIGHT_DOMAIN, ColorMode
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticDeviceEntity
from .model import DeviceType, Device

SUPPORTED_DEVICE_TYPES = [
    DeviceType.LIGHT,
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up light platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device, area_name in synthetic_home.devices_and_areas(SUPPORTED_DEVICE_TYPES):
        if device.device_type == DeviceType.LIGHT:
            entities.append(SyntheticHomeLight(device, area_name, **device.attributes))

    async_add_devices(entities, True)


class SyntheticHomeLight(SyntheticDeviceEntity, LightEntity):
    """synthetic_home light class."""

    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(
        self,
        device: Device,
        area: str,
        *,
        brightness: int | None = None
    ) -> None:
        """Initialize the climate device."""
        super().__init__(device, area, "light")
        self._attr_brightness = brightness


    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the light."""
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
