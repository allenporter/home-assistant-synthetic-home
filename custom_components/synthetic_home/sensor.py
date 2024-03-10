"""Sensor platform for Synthetic Home."""

import logging

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
from .model import ParsedHome, ParsedDevice
from .entity import SyntheticDeviceEntity

_LOGGER = logging.getLogger(__name__)


class SyntheticSensorEntityDescription(SensorEntityDescription, frozen_or_thawed=True):
    """Entity description for a sensor."""

    native_value: StateType | None = None


SENSORS: tuple[SyntheticSensorEntityDescription, ...] = (
    SyntheticSensorEntityDescription(
        key="generic",
        state_class=SensorStateClass.MEASUREMENT,
        native_value=0,
    ),
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

    synthetic_home: ParsedHome = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        SyntheticHomeSensor(device, SENSOR_MAP[entity.entity_key], **entity.attributes)
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == SENSOR_DOMAIN
    )


class SyntheticHomeSensor(SyntheticDeviceEntity, SensorEntity):
    """synthetic_home Sensor class."""

    def __init__(
        self,
        device: ParsedDevice,
        entity_desc: SyntheticSensorEntityDescription,
        *,
        native_value: StateType | None = None,
        native_unit_of_measurement: str | None = None
    ) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(device, entity_desc.key)
        self._attr_name = entity_desc.key.capitalize()
        self.entity_description = entity_desc
        self._attr_native_value = native_value or entity_desc.native_value
        self._attr_native_unit_of_measurement = (
            native_unit_of_measurement or entity_desc.native_unit_of_measurement
        )
