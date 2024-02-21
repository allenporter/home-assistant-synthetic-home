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
  - name: light
    entities:
    - light.family_room
  - name: smart_tv
    entities:
    - media_player.family_room_tv
    - remote.family_room_tv
    - binary_sensor.family_room_tv_headphones_connected
"""


TEST_ENTITY = "binary_sensor.smart_tv_family_room_tv_headphones_connected"


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up switch platform."""
    return [Platform.BINARY_SENSOR]


@pytest.fixture
def config_yaml() -> None:
    """Mock out the yaml config file contents."""
    return TEST_YAML


async def test_sensor(hass: HomeAssistant, setup_integration: None) -> None:
    """Test sensor."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Smart Tv Family room tv headphones connected"
    }
