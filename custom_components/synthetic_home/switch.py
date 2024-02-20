"""Switch platform for Synthetic Home."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.switch import SwitchEntity, DOMAIN as SWITCH_DOMAIN
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DEFAULT_NAME, DOMAIN


ICON = "mdi:switch"
SWITCH = "switch"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up sensor platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeBinarySwitch(entity_id, device_name, area_name)
        for entity_id, device_name, area_name in synthetic_home.entities_by_domain(SWITCH_DOMAIN)
    )


class SyntheticHomeBinarySwitch(SwitchEntity):
    """synthetic_home switch class."""

    def __init__(self, entity_id: str, device_name: str, suggested_area: str) -> None:
        """Initialize SyntheticHomeBinarySwitch."""
        self.entity_id = entity_id
        self._attr_device_info = DeviceInfo(
            name=device_name,
            suggested_area=suggested_area,
        )


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
