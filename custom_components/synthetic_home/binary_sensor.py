"""Binary sensor platform for Synthetic Home."""

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
    DOMAIN as BINARY_SENSOR_DOMAIN,
)

from .const import DOMAIN
from .model import ParsedDevice
from .entity import SyntheticDeviceEntity


BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="lock",
        device_class=BinarySensorDeviceClass.LOCK,
    ),
    BinarySensorEntityDescription(
        key="door",
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    BinarySensorEntityDescription(
        key="window",
        device_class=BinarySensorDeviceClass.WINDOW,
    ),
    BinarySensorEntityDescription(
        key="tamper",
        device_class=BinarySensorDeviceClass.TAMPER,
    ),
    BinarySensorEntityDescription(
        key="battery",
        device_class=BinarySensorDeviceClass.BATTERY,
    ),
    BinarySensorEntityDescription(
        key="motion",
        device_class=BinarySensorDeviceClass.MOTION,
    ),
)
SENSOR_MAP = {desc.key: desc for desc in BINARY_SENSORS}


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up binary_sensor platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeBinarySensor(device, SENSOR_MAP[entity.entity_key])
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == BINARY_SENSOR_DOMAIN
    )


class SyntheticHomeBinarySensor(SyntheticDeviceEntity, BinarySensorEntity):
    """synthetic_home binary_sensor class."""

    def __init__(
        self,
        device: ParsedDevice,
        entity_desc: BinarySensorEntityDescription,
    ) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(device, entity_desc.key)
        if entity_desc.key not in device.friendly_name.lower():  # Avoid "Motion Motion"
            self._attr_name = entity_desc.key.capitalize()
        self.entity_description = entity_desc

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return False
