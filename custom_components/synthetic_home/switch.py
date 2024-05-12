"""Switch platform for Synthetic Home."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.switch import (
    SwitchEntity,
    SwitchDeviceClass,
    DOMAIN as SWITCH_DOMAIN,
    SwitchEntityDescription,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityDescription

from .const import DOMAIN
from .entity import SyntheticDeviceEntity
from .model import ParsedDevice


SWITCHES: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key="outlet",
        device_class=SwitchDeviceClass.OUTLET,
    ),
    SwitchEntityDescription(
        key="switch",
        device_class=SwitchDeviceClass.SWITCH,
    ),
)
SENSOR_MAP = {desc.key: desc for desc in SWITCHES}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up switch platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeBinarySwitch(device, SENSOR_MAP[entity.entity_key])
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == SWITCH_DOMAIN
    )


class SyntheticHomeBinarySwitch(SyntheticDeviceEntity, SwitchEntity):
    """synthetic_home switch class."""

    def __init__(
        self,
        device: ParsedDevice,
        entity_desc: SwitchEntityDescription,
    ) -> None:
        """Initialize SyntheticHomeBinarySwitch."""
        super().__init__(device, entity_desc.key)
        self._attr_name = entity_desc.key.capitalize()
        self.entity_description = entity_desc

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
