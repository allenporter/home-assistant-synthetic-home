"""Test Synthetic Home weather."""

import pytest

from homeassistant.const import Platform
from homeassistant.components.weather import (
    DOMAIN as WEATHER_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .conftest import FIXTURES

TEST_ENTITY = "weather.home"


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up test platform."""
    return [Platform.WEATHER]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/weather-example.yaml", TEST_ENTITY)],
)
async def test_weather_entity(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test weather entity."""

    state = hass.states.get(test_entity)
    assert state
    # Fair conditions
    assert state.state == "sunny"
    assert state.attributes.get("friendly_name") == "Home"
    assert state.attributes.get("humidity") == 60
    assert state.attributes.get("temperature") == 22.2
    assert state.attributes.get("temperature_unit") == "°C"
    assert state.attributes.get("wind_speed") == 8.05
    assert state.attributes.get("wind_speed_unit") == "km/h"

    # Verify daily forecast
    response = await hass.services.async_call(
        WEATHER_DOMAIN,
        "get_forecasts",
        target={ATTR_ENTITY_ID: test_entity, "type": "daily"},
        blocking=True,
        return_response=True,
    )
    await hass.async_block_till_done()
    forecast = response.get(test_entity, {}).get("forecast", [])
    assert [
        (condition.get("condition"), condition.get("temperature"))
        for condition in forecast
    ] == [
        ("cloudy", 15.6),
        ("rainy", 10.0),
    ]

    # Verify hourly forecast
    response = await hass.services.async_call(
        WEATHER_DOMAIN,
        "get_forecasts",
        target={ATTR_ENTITY_ID: test_entity, "type": "hourly"},
        blocking=True,
        return_response=True,
    )
    await hass.async_block_till_done()
    forecast = response.get(test_entity, {}).get("forecast", [])
    assert [
        (condition.get("condition"), condition.get("temperature"))
        for condition in forecast
    ] == [
        ("sunny", 22.2),
        ("sunny", 22.2),
        ("cloudy", 15.6),
        ("cloudy", 15.6),
    ]

    # Verify twice daily forecast
    response = await hass.services.async_call(
        WEATHER_DOMAIN,
        "get_forecasts",
        target={ATTR_ENTITY_ID: test_entity, "type": "twice_daily"},
        blocking=True,
        return_response=True,
    )
    await hass.async_block_till_done()
    forecast = response.get(test_entity, {}).get("forecast", [])
    assert [
        (
            condition.get("condition"),
            condition.get("temperature"),
            condition.get("is_daytime"),
        )
        for condition in forecast
    ] == [
        ("sunny", 22.2, True),
        ("cloudy", 15.6, False),
        ("rainy", 10.0, True),
        ("cloudy", 15.6, False),
    ]
