"""Sensor platform for Synthetic Home."""

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN, SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DEFAULT_NAME, DOMAIN
from .model import generate_entity_unique_id, friendly_device_name, generate_device_id, friendly_entity_name


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up sensor platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        SyntheticHomeSensor(entity_id, device_name, area_name)
        for entity_id, device_name, area_name in synthetic_home.entities_by_domain(
            SENSOR_DOMAIN
        )
    )

class SyntheticHomeSensor(SensorEntity):
    """synthetic_home Sensor class."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entity_id: str, device_name: str, area_name: str) -> None:
        """Initialize SyntheticHomeSensor."""
        self._attr_unique_id = generate_entity_unique_id(
            entity_id, device_name, area_name
        )
        self._attr_name = friendly_entity_name(entity_id)
        #self.entity_id = entity_id
        device_id = generate_device_id(device_name, area_name)
        self._attr_device_info = DeviceInfo(
            name=friendly_device_name(device_name),
            suggested_area=area_name,
            identifiers={(DOMAIN, device_id)},
        )

    @property
    def state(self):
        """Return the state of the sensor."""
        return 0
