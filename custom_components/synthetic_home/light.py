"""Switch platform for Synthetic Home."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity, DOMAIN as LIGHT_DOMAIN
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .model import generate_entity_unique_id, friendly_device_name, generate_device_id


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up light platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeLight(entity_id, device_name, area_name)
        for entity_id, device_name, area_name in synthetic_home.entities_by_domain(
            LIGHT_DOMAIN
        )
    )


class SyntheticHomeLight(LightEntity):
    """synthetic_home light class."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entity_id: str, device_name: str, area_name: str) -> None:
        """Initialize SyntheticHomeLight."""
        self._attr_unique_id = generate_entity_unique_id(
            entity_id, device_name, area_name
        )
        self.entity_id = entity_id
        device_id = generate_device_id(device_name, area_name)
        self._attr_device_info = DeviceInfo(
            name=friendly_device_name(device_name),
            suggested_area=area_name,
            identifiers={(DOMAIN, device_id)},
        )

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
