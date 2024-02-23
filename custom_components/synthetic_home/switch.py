"""Switch platform for Synthetic Home."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticDeviceEntity
from .model import DeviceType

SUPPORTED_DEVICE_TYPES = [DeviceType.SWITCH]

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up switch platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        SyntheticHomeBinarySwitch(device, area_name, "switch")
        for device, area_name in synthetic_home.devices_and_areas(SUPPORTED_DEVICE_TYPES)
    )


class SyntheticHomeBinarySwitch(SyntheticDeviceEntity, SwitchEntity):
    """synthetic_home switch class."""

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        self._attr_state = "on"
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        self._attr_state = "off"
        self.async_write_ha_state()

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._attr_state == "on"
