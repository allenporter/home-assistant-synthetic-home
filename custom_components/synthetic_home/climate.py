"""Climate platform for Synthetic Home."""

from typing import Any

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from .const import DOMAIN
from .model import DeviceType, Device
from .entity import SyntheticDeviceEntity

SUPPORTED_DEVICE_TYPES = {
    DeviceType.CLIMATE_HEAT_PUMP,
    DeviceType.CLIMATE_HVAC,
}
SUPPORT_FLAGS = ClimateEntityFeature(0)
FAN_MODES = ["low", "high", "off"]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up climate platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device, area_name in synthetic_home.devices_and_areas(SUPPORTED_DEVICE_TYPES):
        if device.device_type == DeviceType.CLIMATE_HEAT_PUMP:
            entities.append(
                SyntheticHomeClimate(
                    device,
                    area_name,
                    target_temperature=68,
                    unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
                    current_temperature=77,
                    hvac_mode=HVACMode.HEAT,
                    hvac_action=HVACAction.HEATING,
                    hvac_modes=[HVACMode.HEAT, HVACMode.OFF],
                )
            )
        elif device.device_type == DeviceType.CLIMATE_HVAC:
            entities.append(
                SyntheticHomeClimate(
                    device,
                    area_name,
                    target_temperature=21,
                    unit_of_measurement=UnitOfTemperature.CELSIUS,
                    current_temperature=22,
                    hvac_mode=HVACMode.COOL,
                    hvac_action=HVACAction.COOLING,
                    hvac_modes=[
                        HVACMode.OFF,
                        HVACMode.COOL,
                        HVACMode.HEAT,
                        HVACMode.AUTO,
                    ],
                )
            )

    async_add_devices(entities)


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
        target_temperature: float | None,
        unit_of_measurement: str,
        current_temperature: float,
        hvac_mode: HVACMode,
        hvac_action: HVACAction | None,
        hvac_modes: list[HVACMode],
    ) -> None:
        """Initialize the climate device."""
        super().__init__(device, area, "climate")
        self._attr_supported_features = (
            SUPPORT_FLAGS
            # | ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )
        if HVACMode.HEAT_COOL in hvac_modes or HVACMode.AUTO in hvac_modes:
            self._attr_supported_features |= (
                ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
            )
        self._attr_supported_features |= (
            ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        )
        self._attr_target_temperature = target_temperature
        self._attr_temperature_unit = unit_of_measurement
        self._attr_target_temperature_high = None
        self._attr_target_temperature_low = None
        self._attr_current_temperature = current_temperature
        self._attr_hvac_action = hvac_action
        self._attr_hvac_mode = hvac_mode
        self._attr_hvac_modes = hvac_modes

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
