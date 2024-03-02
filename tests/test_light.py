"""Test Synthetic Home switch."""

import pytest

from homeassistant.const import Platform
from homeassistant.components.light import (
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    DOMAIN as LIGHT_DOMAIN,
    ATTR_BRIGHTNESS,
    ATTR_RGBW_COLOR,
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


@pytest.mark.parametrize(
        "config_yaml_fixture",
        [(f"{FIXTURES}/light-example.yaml")],
)
async def test_light(hass: HomeAssistant, setup_integration: None) -> None:
    """Test light entity."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Family Room",
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
    assert state.attributes == {
        "friendly_name": "Family Room",
        "color_mode": "onoff",
        "supported_color_modes":  ["onoff"],
        "supported_features": 0,
    }


@pytest.mark.parametrize(
        "config_yaml_fixture",
        [(f"{FIXTURES}/light-dimmable.yaml")],
)
async def test_dimmable_light(hass: HomeAssistant, setup_integration: None) -> None:
    """Test a dimmable light entity."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "brightness": None,
        "friendly_name": "Family Room",
        "color_mode": None,
        "supported_color_modes": ["brightness"],
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
    assert state.attributes == {
        "brightness": 30,
        "friendly_name": "Family Room",
        "color_mode": "brightness",
        "supported_color_modes":  ["brightness"],
        "supported_features": 0,
    }

    # Lower brightness
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        service_data={ATTR_ENTITY_ID: TEST_ENTITY, ATTR_BRIGHTNESS: 15},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "on"
    assert state.attributes == {
        "brightness": 15,
        "friendly_name": "Family Room",
        "color_mode": "brightness",
        "supported_color_modes":  ["brightness"],
        "supported_features": 0,
    }



@pytest.mark.parametrize(
        "config_yaml_fixture",
        [(f"{FIXTURES}/light-rgbw.yaml")],
)
async def test_rgbw_light(hass: HomeAssistant, setup_integration: None) -> None:
    """Test a light entity with rgbw color mode."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "brightness": None,
        "friendly_name": "Family Room",
        "color_mode": None,
        "hs_color": None,
        "rgb_color": None,
        "rgbw_color": None,
        "supported_color_modes": ["rgbw"],
        "supported_features": 0,
        "xy_color": None,
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
    assert state.attributes == {
        "brightness": None,
        "friendly_name": "Family Room",
        "color_mode": "rgbw",
        "hs_color": (60, 49.804),
        "rgb_color": (255, 255, 128),
        "rgbw_color": (255, 255, 0, 255),
        "supported_color_modes":  ["rgbw"],
        "supported_features": 0,
        "xy_color": (0.406, 0.458),
    }

    # Change light color
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        service_data={ATTR_ENTITY_ID: TEST_ENTITY, ATTR_RGBW_COLOR: (0, 0, 255, 255)},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "on"
    assert state.attributes == {
        "brightness": None,
        "friendly_name": "Family Room",
        "color_mode": "rgbw",
        "hs_color": (240.0, 49.804),
        "rgb_color": (128, 128, 255),
        "rgbw_color": (0, 0, 255, 255),
        "supported_color_modes":  ["rgbw"],
        "supported_features": 0,
        "xy_color": (0.213, 0.159),
    }


@pytest.mark.parametrize(
        "config_yaml_fixture",
        [(f"{FIXTURES}/garage-door-example.yaml")],
)
async def test_garage_door(hass: HomeAssistant, setup_integration: None) -> None:
    """Test light entity."""

    state = hass.states.get("light.garage_door")
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Garage Door",
        "color_mode": None,
        "supported_color_modes": ["onoff"],
        "supported_features": 0,
    }
