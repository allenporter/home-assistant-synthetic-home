"""Switch platform for Synthetic Home."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity, DOMAIN as LIGHT_DOMAIN, ColorMode, ATTR_BRIGHTNESS, ATTR_RGBW_COLOR
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticDeviceEntity
from .model import DeviceType, Device

SUPPORTED_DEVICE_TYPES = [
    DeviceType.LIGHT,
    DeviceType.LIGHT_DIMMABLE,
    DeviceType.LIGHT_RGBW,
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up light platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device, area_name in synthetic_home.devices_and_areas(SUPPORTED_DEVICE_TYPES):
        if device.device_type == DeviceType.LIGHT_DIMMABLE:
            entities.append(
                SyntheticHomeLight(
                    device,
                    area_name,
                    supported_color_modes={ColorMode.BRIGHTNESS},
                    color_mode=ColorMode.BRIGHTNESS,
                    **device.attributes
                )
            )
        if device.device_type == DeviceType.LIGHT:
            entities.append(
                SyntheticHomeLight(
                    device,
                    area_name,
                    supported_color_modes={ColorMode.ONOFF},
                    color_mode=ColorMode.ONOFF,
                    **device.attributes
                )
            )
        if device.device_type == DeviceType.LIGHT_RGBW:
            entities.append(
                SyntheticHomeLight(
                    device,
                    area_name,
                    supported_color_modes={ColorMode.RGBW},
                    color_mode=ColorMode.RGBW,
                    **device.attributes
                )
            )
    async_add_devices(entities, True)


class SyntheticHomeLight(SyntheticDeviceEntity, LightEntity):
    """synthetic_home light class."""

    def __init__(
        self,
        device: Device,
        area: str,
        *,
        supported_color_modes: set[ColorMode] | None = None,
        color_mode: ColorMode | None = None,
        brightness: int | None = None,
        rgbw_color: tuple[int, int, int, int] | None = None,
    ) -> None:
        """Initialize the climate device."""
        super().__init__(device, area, "light")
        self._attr_supported_color_modes = supported_color_modes
        self._attr_color_mode = color_mode
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
