"""Test Synthetic Home sensor."""

import pytest

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

TEST_YAML = """
---
name: Family Farmhouse
country_code: US
location: Rural area in Iowa
type: Farmhouse
device_entities:
  Family Room:
  - name: thermostat
    entities:
    - climate.family_room
    - sensor.family_room_temperature
    - sensor.family_room_humidity
"""


TEST_ENTITY = "sensor.thermostat_family_room_temperature"


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up switch platform."""
    return [Platform.SENSOR]


@pytest.fixture
def config_yaml() -> None:
    """Mock out the yaml config file contents."""
    return TEST_YAML


async def test_sensor(hass: HomeAssistant, setup_integration: None) -> None:
    """Test sensor."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "0"
    assert state.attributes == {
        "friendly_name": "Thermostat Family room temperature"
    }
