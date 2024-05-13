"""Binary sensor platform for Synthetic Home."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
    DOMAIN as BINARY_SENSOR_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant

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
    BinarySensorEntityDescription(
        key="person",
        device_class=BinarySensorDeviceClass.OCCUPANCY,
    ),
    BinarySensorEntityDescription(
        key="sound",
        device_class=BinarySensorDeviceClass.SOUND,
    ),
)
SENSOR_MAP = {desc.key: desc for desc in BINARY_SENSORS}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up binary_sensor platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeBinarySensor(
            device, SENSOR_MAP[entity.entity_key], **entity.attributes
        )
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
        *,
        is_on: bool = False,
    ) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(device, entity_desc.key)
        if entity_desc.key not in device.friendly_name.lower():  # Avoid "Motion Motion"
            self._attr_name = entity_desc.key.capitalize()
        self.entity_description = entity_desc
        self._attr_is_on = is_on
