"""Weather platform for Synthetic Home."""

import datetime
from dataclasses import dataclass
import logging
from typing import Any

from synthetic_home import device_types


from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
    DOMAIN as WEATHER_DOMAIN,
    Forecast,
)
from homeassistant.util import dt as dt_util
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .model import ParsedHome, ParsedEntity, filter_attributes
from .entity import SyntheticEntity


_LOGGER = logging.getLogger(__name__)


SUPPORTED_ATTRIBUTES = set(
    {
        "condition",
        "native_temperature",
        "native_temperature_unit",
        "humidity",
        "native_wind_speed",
        "native_wind_speed_unit",
        "daily_forecast",
        "hourly_forecast",
        "twice_daily_forecast",
    }
)


@dataclass
class WeatherCondition:
    """Definition of a weather condition.

    The condition can be used either for the current state of the weather entity
    or for forecast data in the future.
    """

    condition: str | None = None
    native_temperature: float | None = None
    temperature_unit_of_measurement: str | None = None
    humidity: float | None = None
    native_wind_speed: float | None = None
    wind_speed_unit_of_measurement: str | None = None

    def as_forecast(self, dt: datetime.datetime) -> Forecast:
        """Convert the WeatherCondition to a forecast."""
        return Forecast(
            datetime=dt.isoformat(),
            condition=self.condition,
            native_temperature=self.native_temperature,
            humidity=self.humidity,
            native_wind_speed=self.native_wind_speed,
        )


FORECAST_TYPES = [
    "daily_forecast",
    "hourly_forecast",
    "twice_daily_forecast",
]

def map_attributes(
    entity: ParsedEntity,
    condition_map: dict[str, device_types.DeviceState],
) -> dict[str, Any]:
    """Override some specific weather forecast attributes."""
    result = {}
    for k, v in entity.attributes.items():
        if k == "temperature":
            k = "current_temperature"
        result[k] = v

    for forecast_key in FORECAST_TYPES:
        if daily_forecast := result.get(forecast_key):
            conditions = []
            for key in daily_forecast:
                if not (condition := condition_map.get(key)):
                    raise ValueError(f"Could not find weather condition '{key}'")
                if not condition.entity_states:
                    raise ValueError(
                        f"Could not load condition entity state for '{key}'"
                    )
                entity_state = condition.entity_states[0].state
                if not isinstance(entity_state, dict):
                    raise TypeError(
                        f"Could not load entity state for '{key}', required dict for entity_state condition"
                    )
                conditions.append(WeatherCondition(**entity_state))
            result[forecast_key] = conditions
    entity.attributes = result
    return filter_attributes(entity, SUPPORTED_ATTRIBUTES)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up weather platform."""
    synthetic_home: ParsedHome = hass.data[DOMAIN][entry.entry_id]

    registry = device_types.load_device_type_registry()
    weather_service: device_types.DeviceType = registry.device_types["weather-service"]

    async_add_devices(
        SyntheticHomeWeather(
            entity,
            **map_attributes(entity, weather_service.device_states_dict),
        )
        for entity in synthetic_home.entities
        if entity.platform == WEATHER_DOMAIN
    )




class SyntheticHomeWeather(SyntheticEntity, WeatherEntity):
    """synthetic_home Weather class."""

    _attr_supported_features = 0

    def __init__(
        self,
        entity: ParsedEntity,
        *,
        condition: str | None = None,
        native_temperature: float | None = None,
        native_temperature_unit: str | None = None,
        humidity: float | None = None,
        native_wind_speed: float | None = None,
        native_wind_speed_unit: str | None = None,
        daily_forecast: list[WeatherCondition] | None = None,
        hourly_forecast: list[WeatherCondition] | None = None,
        twice_daily_forecast: list[WeatherCondition] | None = None,
    ) -> None:
        """Initialize SyntheticHomeWeather."""
        super().__init__(entity)
        self._attr_condition = condition
        self._attr_native_temperature = native_temperature
        self._attr_native_temperature_unit = native_temperature_unit
        self._attr_humidity = humidity
        self._attr_native_wind_speed = native_wind_speed
        self._attr_native_wind_speed_unit = native_wind_speed_unit

        if daily_forecast:
            self._daily_forecast = daily_forecast
            self._attr_supported_features |= WeatherEntityFeature.FORECAST_DAILY
        if hourly_forecast:
            self._hourly_forecast = hourly_forecast
            self._attr_supported_features |= WeatherEntityFeature.FORECAST_HOURLY
        if twice_daily_forecast:
            self._twice_daily_forecast = twice_daily_forecast
            self._attr_supported_features |= WeatherEntityFeature.FORECAST_TWICE_DAILY

    async def async_forecast_daily(self) -> list[Forecast]:
        """Return the daily forecast."""
        reftime = dt_util.now().replace(hour=16, minute=00)

        forecast_data = []
        for condition in self._daily_forecast:
            data_dict = condition.as_forecast(reftime)
            reftime = reftime + datetime.timedelta(hours=24)
            forecast_data.append(data_dict)

        return forecast_data

    async def async_forecast_hourly(self) -> list[Forecast]:
        """Return the hourly forecast."""
        reftime = dt_util.now().replace(hour=16, minute=00)

        forecast_data = []
        for condition in self._hourly_forecast:
            data_dict = condition.as_forecast(reftime)
            reftime = reftime + datetime.timedelta(hours=1)
            forecast_data.append(data_dict)

        return forecast_data

    async def async_forecast_twice_daily(self) -> list[Forecast]:
        """Return the twice daily forecast."""
        reftime = dt_util.now().replace(hour=11, minute=00)

        forecast_data = []
        for condition in self._twice_daily_forecast:
            data_dict = condition.as_forecast(reftime)
            data_dict["is_daytime"] = 6 <= reftime.hour <= 20
            reftime = reftime + datetime.timedelta(hours=12)
            forecast_data.append(data_dict)

        return forecast_data
