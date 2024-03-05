"""Sensor platform for Synthetic Home."""

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
    StateType,
    DOMAIN as SENSOR_DOMAIN,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfEnergy

from .const import DOMAIN
from .model import Device
from .entity import SyntheticDeviceEntity


class SyntheticSensorEntityDescription(SensorEntityDescription, frozen_or_thawed=True):
    """Entity description for a sensor."""

    native_value: StateType | None = None


SENSORS: tuple[SyntheticSensorEntityDescription, ...] = (
    SyntheticSensorEntityDescription(
        key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_value=20,
    ),
    SyntheticSensorEntityDescription(
        key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_value=45,
    ),
    SyntheticSensorEntityDescription(
        key="energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_value=1,
    ),
    SyntheticSensorEntityDescription(
        key="battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_value=90,
    ),
)
SENSOR_MAP = {desc.key: desc for desc in SENSORS}


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up sensor platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device, area_name, key in synthetic_home.devices_and_areas(SENSOR_DOMAIN):
        entities.append(SyntheticHomeSensor(device, area_name, SENSOR_MAP[key]))

    async_add_devices(entities)


class SyntheticHomeSensor(SyntheticDeviceEntity, SensorEntity):
    """synthetic_home Sensor class."""

    def __init__(
        self,
        device: Device,
        area_name: str,
        entity_desc: SyntheticSensorEntityDescription,
        *,
        native_value: StateType | None = None,
    ) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(device, area_name, entity_desc.key)
        self._attr_name = entity_desc.key.capitalize()
        self.entity_description = entity_desc
        self._attr_native_value = native_value or entity_desc.native_value
