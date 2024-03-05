"""Switch platform for Synthetic Home."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.switch import (
    SwitchEntity,
    SwitchDeviceClass,
    DOMAIN as SWITCH_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityDescription

from .const import DOMAIN
from .entity import SyntheticDeviceEntity
from .model import Device


SWITCHES: tuple[EntityDescription, ...] = (
    EntityDescription(
        key="outlet",
        device_class=SwitchDeviceClass.OUTLET,
    ),
    EntityDescription(
        key="switch",
        device_class=SwitchDeviceClass.SWITCH,
    ),
)
SENSOR_MAP = {desc.key: desc for desc in SWITCHES}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up switch platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device, area_name, key in synthetic_home.devices_and_areas(SWITCH_DOMAIN):
        entities.append(SyntheticHomeBinarySwitch(device, area_name, SENSOR_MAP[key]))
    async_add_devices(entities)


class SyntheticHomeBinarySwitch(SyntheticDeviceEntity, SwitchEntity):
    """synthetic_home switch class."""

    def __init__(
        self,
        device: Device,
        area_name: str,
        entity_desc: EntityDescription,
    ) -> None:
        """Initialize SyntheticHomeBinarySwitch."""
        super().__init__(device, area_name, entity_desc.key)
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
