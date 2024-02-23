"""Test Synthetic Home sensor."""

import pytest

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .conftest import FIXTURES

TEST_FIXTURE_FILE = f"{FIXTURES}/binary-sensor-motion.yaml"

TEST_ENTITY = "binary_sensor.motion_sensor"


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up switch platform."""
    return [Platform.BINARY_SENSOR]


@pytest.fixture
def config_yaml_fixture() -> None:
    """Mock out the yaml config file contents."""
    return TEST_FIXTURE_FILE


async def test_motion_sensor(hass: HomeAssistant, setup_integration: None) -> None:
    """Test a binary sesnor that detects motion."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Motion Sensor",
        "device_class": "motion",
    }
