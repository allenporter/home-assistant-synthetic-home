"""Climate platform for Synthetic Home."""

from typing import Any
import logging


from homeassistant.config_entries import ConfigEntry
from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
    DOMAIN as CLIMATE_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_TEMPERATURE

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes

_LOGGER = logging.getLogger(__name__)

FAN_MODES = ["low", "high", "off"]
SUPPORTED_ATTRIBUTES = {
    "hvac_modes",
    "supported_features",
    "temperature_unit",
    "unit_of_measurement",
    "current_temperature",
    "target_temperature",
    "hvac_mode",
    "hvac_action",
}
DEFAULT_TEMPERATURE_UNIT = "\xB0F"


def map_attributes(entity: ParsedEntity) -> dict[str, Any]:
    """Convert attributes from home assistant exports to the class here."""
    result = {}
    for k, v in entity.attributes.items():
        if k == "temperature":
            k = "current_temperature"
        result[k] = v
    entity.attributes = result
    return filter_attributes(entity, SUPPORTED_ATTRIBUTES)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up climate platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeClimate(
            entity,
            state=entity.state,
            **map_attributes(entity),
        )
        for entity in synthetic_home.entities
        if entity.platform == CLIMATE_DOMAIN
    )


class SyntheticHomeClimate(SyntheticEntity, ClimateEntity):
    """Representation of a demo climate device."""

    _attr_should_poll = False
    _attr_fan_modes = FAN_MODES
    _attr_fan_mode = None
    _attr_current_fan_mode = "off"

    def __init__(
        self,
        entity: ParsedEntity,
        state: HVACMode | None,
        *,
        hvac_modes: list[HVACMode] | None = None,
        supported_features: ClimateEntityFeature | None = None,
        temperature_unit: str | None = None,
        unit_of_measurement: str | None = None,
        current_temperature: float | None = None,
        target_temperature: float | None = None,
        hvac_mode: HVACMode | None = None,
        hvac_action: HVACAction | None = None,
        preset_modes: list[str] | None = None,
        preset_mode: str | None = None,
    ) -> None:
        """Initialize the climate device."""
        super().__init__(entity)
        if supported_features is not None:
            self._attr_supported_features = ClimateEntityFeature(0) | supported_features
        self._attr_target_temperature = target_temperature
        self._attr_target_temperature_high = None
        self._attr_target_temperature_low = None
        self._attr_current_temperature = current_temperature
        self._attr_hvac_action = hvac_action
        self._attr_hvac_mode = state or hvac_mode
        self._attr_preset_mode = preset_mode
        self._attr_preset_modes = preset_modes
        if hvac_modes is not None:
            self._attr_hvac_modes = hvac_modes
        else:
            self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]
        self._attr_temperature_unit = (
            temperature_unit or unit_of_measurement or DEFAULT_TEMPERATURE_UNIT
        )

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
