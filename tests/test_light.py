"""Test Synthetic Home switch."""

import pytest

from homeassistant.const import Platform
from homeassistant.components.light import (
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    DOMAIN as LIGHT_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .conftest import FIXTURES

TEST_FIXTURE_FILE = f"{FIXTURES}/light-example.yaml"
TEST_ENTITY = "light.family_room"


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up switch platform."""
    return [Platform.LIGHT]


@pytest.fixture
def config_yaml_fixture() -> None:
    """Mock out the yaml config file contents."""
    return TEST_FIXTURE_FILE


async def test_light_services(hass: HomeAssistant, setup_integration: None) -> None:
    """Test switch services."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Light",
        "color_mode": None,
        "supported_color_modes": ["onoff"],
        "supported_features": 0,
    }

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        service_data={ATTR_ENTITY_ID: TEST_ENTITY},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "off"

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        service_data={ATTR_ENTITY_ID: TEST_ENTITY},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "on"
