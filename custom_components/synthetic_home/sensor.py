"""Sensor platform for Synthetic Home."""

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfEnergy

from .const import DOMAIN
from .model import DeviceType, Device
from .entity import SyntheticDeviceEntity


SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)
SENSOR_MAP = {desc.key: desc for desc in SENSORS}

FEATURES: dict[DeviceType, set[str]] = {
    DeviceType.CLIMATE_HVAC: {"temperature", "humidity"},
    DeviceType.SMART_PLUG: {"energy"},
    DeviceType.SMART_LOCK: {"battery"},
    DeviceType.DOOR_SENSOR: {"battery"},
    DeviceType.WINDOW_SENSOR: {"battery"},
    DeviceType.MOTION_SENSOR: {"battery"},
}
SUPPORTED_DEVICE_TYPES = FEATURES.keys()


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up sensor platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device, area_name in synthetic_home.devices_and_areas(SUPPORTED_DEVICE_TYPES):
        for key in FEATURES.get(device.device_type, set({})):
            entities.append(SyntheticHomeSensor(device, area_name, SENSOR_MAP[key]))

    async_add_devices(entities)


class SyntheticHomeSensor(SyntheticDeviceEntity, SensorEntity):
    """synthetic_home Sensor class."""

    def __init__(
        self,
        device: Device,
        area_name: str,
        entity_desc: SensorEntityDescription,
    ) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(device, area_name, entity_desc.key)
        self._attr_name = entity_desc.key.capitalize()
        self.entity_description = entity_desc

    @property
    def state(self):
        """Return the state of the sensor."""
        return 0
