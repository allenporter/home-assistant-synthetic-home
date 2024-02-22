"""Test Synthetic Home sensor."""

import pytest

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant


from .conftest import FIXTURES

TEST_FIXTURE_FILE = f"{FIXTURES}/sensor-example.yaml"

TEST_ENTITY = "sensor.thermostat_family_room_temperature"


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up switch platform."""
    return [Platform.SENSOR]


@pytest.fixture
def config_yaml_fixture() -> None:
    """Mock out the yaml config file contents."""
    return TEST_FIXTURE_FILE


async def test_sensor(hass: HomeAssistant, setup_integration: None) -> None:
    """Test sensor."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "0"
    assert state.attributes == {
        "friendly_name": "Thermostat Family room temperature"
    }
