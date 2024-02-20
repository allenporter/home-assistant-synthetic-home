"""Switch platform for Synthetic Home."""
from homeassistant.components.switch import SwitchEntity

from .const import DEFAULT_NAME


ICON = "mdi:switch"
SWITCH = "switch"


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up sensor platform."""
    async_add_devices([SyntheticHomeBinarySwitch()])


class SyntheticHomeBinarySwitch(SwitchEntity):
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
    def name(self):
        """Return the name of the switch."""
        return DEFAULT_NAME

    @property
    def icon(self):
        """Return the icon of this switch."""
        return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._attr_state == "on"
