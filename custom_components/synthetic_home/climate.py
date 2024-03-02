"""Climate platform for Synthetic Home."""

from typing import Any


from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ClimateEntity,
    ClimateEntityFeature,
    ClimateEntityDescription,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE

from .const import DOMAIN
from .model import DeviceType, Device
from .entity import SyntheticDeviceEntity


DEFAULT_SUPPORTED_FEATURES = (
    ClimateEntityFeature(0)
    | ClimateEntityFeature.FAN_MODE
    | ClimateEntityFeature.TURN_ON
    | ClimateEntityFeature.TURN_OFF
)


class SyntheticClimateEntityDescription(
    ClimateEntityDescription, frozen_or_thawed=True
):
    """A class that describes climate entities."""

    supported_features: ClimateEntityFeature | None = None
    target_temperature: float | None = None
    current_temperature: float | None = None
    hvac_mode: HVACMode | None = None
    hvac_action: HVACAction | None | None = None
    hvac_modes: list[HVACMode] | None = None


CLIMATES: tuple[SyntheticClimateEntityDescription, ...] = (
    SyntheticClimateEntityDescription(
        key="heat-pump",
        supported_features=DEFAULT_SUPPORTED_FEATURES,
        target_temperature=68,
        hvac_mode=HVACMode.HEAT,
        hvac_action=HVACAction.HEATING,
        hvac_modes=[HVACMode.HEAT, HVACMode.OFF],
    ),
    SyntheticClimateEntityDescription(
        key="hvac",
        supported_features=(
            DEFAULT_SUPPORTED_FEATURES | ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        ),
        target_temperature=21,
        hvac_mode=HVACMode.COOL,
        hvac_action=HVACAction.COOLING,
        hvac_modes=[
            HVACMode.OFF,
            HVACMode.COOL,
            HVACMode.HEAT,
            HVACMode.AUTO,
        ],
    ),
)
CLIMATE_MAP = {desc.key: desc for desc in CLIMATES}

FEATURES: dict[DeviceType, str] = {
    DeviceType.HEAT_PUMP: "heat-pump",
    DeviceType.HVAC: "hvac",
}
SUPPORTED_DEVICE_TYPES = FEATURES.keys()

FAN_MODES = ["low", "high", "off"]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up climate platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device, area_name in synthetic_home.devices_and_areas(SUPPORTED_DEVICE_TYPES):
        key = FEATURES[device.device_type]
        entity_desc = CLIMATE_MAP[key]
        entities.append(
            SyntheticHomeClimate(device, area_name, entity_desc, **device.attributes)
        )
    async_add_devices(entities, True)


class SyntheticHomeClimate(SyntheticDeviceEntity, ClimateEntity):
    """Representation of a demo climate device."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False
    _attr_fan_modes = FAN_MODES
    _attr_fan_mode = None
    _attr_current_fan_mode = "off"

    def __init__(
        self,
        device: Device,
        area: str,
        entity_desc: SyntheticClimateEntityDescription,
        *,
        unit_of_measurement: str | None = None,
        current_temperature: float | None = None,
    ) -> None:
        """Initialize the climate device."""
        super().__init__(device, area, entity_desc.key)
        self.entity_description = entity_desc
        self._attr_supported_features = entity_desc.supported_features
        self._attr_target_temperature = entity_desc.target_temperature
        self._attr_target_temperature_high = None
        self._attr_target_temperature_low = None
        self._attr_current_temperature = (
            current_temperature or entity_desc.current_temperature
        )
        self._attr_hvac_action = entity_desc.hvac_action
        self._attr_hvac_mode = entity_desc.hvac_mode
        self._attr_hvac_modes = entity_desc.hvac_modes
        self._attr_temperature_unit = unit_of_measurement

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._attr_target_temperature = kwargs.get(ATTR_TEMPERATURE)
        if (
            kwargs.get(ATTR_TARGET_TEMP_HIGH) is not None
            and kwargs.get(ATTR_TARGET_TEMP_LOW) is not None
        ):
            self._attr_target_temperature_high = kwargs.get(ATTR_TARGET_TEMP_HIGH)
            self._attr_target_temperature_low = kwargs.get(ATTR_TARGET_TEMP_LOW)
        if (hvac_mode := kwargs.get(ATTR_HVAC_MODE)) is not None:
            self._attr_hvac_mode = hvac_mode
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        self._attr_current_fan_mode = fan_mode
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        self._attr_hvac_mode = hvac_mode
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Update preset_mode on."""
        self._attr_preset = preset_mode
        self.async_write_ha_state()
