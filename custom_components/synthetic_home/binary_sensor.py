"""Binary sensor platform for Synthetic Home."""

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN, BinarySensorEntity

from .const import DOMAIN
from .model import friendly_entity_name
from .entity import SyntheticEntity

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up binary_sensor platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        SyntheticHomeBinarySensor(entity_id, device_name, area_name)
        for entity_id, device_name, area_name in synthetic_home.entities_by_domain(
            BINARY_SENSOR_DOMAIN
        )
    )


class SyntheticHomeBinarySensor(SyntheticEntity, BinarySensorEntity):
    """synthetic_home binary_sensor class."""

    def __init__(self, entity_id: str, device_name: str, area_name: str) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(entity_id, device_name, area_name)
        self.entity_id = None
        self._attr_name = friendly_entity_name(entity_id)

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return False
