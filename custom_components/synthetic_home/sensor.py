"""Sensor platform for Synthetic Home."""

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN, SensorEntity

from .const import DOMAIN
from .model import friendly_entity_name
from .entity import SyntheticEntity

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up sensor platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        SyntheticHomeSensor(entity_id, device_name, area_name)
        for entity_id, device_name, area_name in synthetic_home.entities_by_domain(
            SENSOR_DOMAIN
        )
    )

class SyntheticHomeSensor(SyntheticEntity, SensorEntity):
    """synthetic_home Sensor class."""

    def __init__(self, entity_id: str, device_name: str, area_name: str) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(entity_id, device_name, area_name)
        self.entity_id = None
        self._attr_name = friendly_entity_name(entity_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return 0
