"""Test Synthetic Home climate entity."""

import pytest

from homeassistant.const import Platform
from homeassistant.components.climate import (
    SERVICE_SET_TEMPERATURE,
    SERVICE_SET_HVAC_MODE,
    DOMAIN as CLIMATE_DOMAIN,
    ATTR_HVAC_MODE
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant

TEST_YAML = """
---
name: Family Farmhouse
country_code: US
location: Rural area in Iowa
type: Farmhouse
device_entities:
  Family room:
  - name: Family room
    unique_id: d4df546410f90f1c1d9be6a8443b8ec6
    device_type: climate_hvac
    device_info:
        model: Thermostat
        manufacturer: Nest
        firmware: 1.0.0
    attributes:
        unit_of_measurement: F
        temperature: 60
"""


TEST_ENTITY = "climate.family_room"


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up switch platform."""
    return [Platform.CLIMATE]


@pytest.fixture
def config_yaml() -> None:
    """Mock out the yaml config file contents."""
    return TEST_YAML


async def test_climate_hvac_entity(
    hass: HomeAssistant, setup_integration: None
) -> None:
    """Test switch services."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "cool"
    assert state.attributes == {
        "friendly_name": "Family Room",
        "current_temperature": 22,
        "fan_mode": None,
        "fan_modes": ["low", "high", "off"],
        "hvac_action": "cooling",
        "hvac_modes": ["off", "cool", "heat", "auto"],
        "max_temp": 35,
        "min_temp": 7,
        "supported_features": 394,
        "target_temp_high": None,
        "target_temp_low": None,
    }
    attributes = dict(state.attributes)

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {ATTR_ENTITY_ID: TEST_ENTITY, ATTR_HVAC_MODE: "heat"},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "heat"
    assert state.attributes == attributes
