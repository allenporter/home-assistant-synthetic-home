"""Test Synthetic Home cover."""

import datetime

import pytest


from homeassistant.const import Platform
from homeassistant.components.cover import (
    DOMAIN as COVER_DOMAIN,
    SERVICE_OPEN_COVER,
    SERVICE_CLOSE_COVER,
    SERVICE_SET_COVER_POSITION,
    ATTR_POSITION
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from .conftest import FIXTURES

TEST_FIXTURE_FILE = f"{FIXTURES}/covers-example.yaml"
TEST_COVER_ENTITY = "cover.garage_door"
TEST_COVER_POSITIONABLE_ENTITY = "cover.left_shade"

@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.COVER]

@pytest.fixture
def config_yaml_fixture() -> None:
    """Mock out the yaml config file contents."""
    return TEST_FIXTURE_FILE


async def test_cover(hass: HomeAssistant, setup_integration: None) -> None:
    """Test cover services."""

    state = hass.states.get(TEST_COVER_ENTITY)
    assert state
    assert state.state == "closed"
    assert state.attributes == {
        "friendly_name": "Garage Door",
        "current_position": 0,
        "supported_features": 3,
    }

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_OPEN_COVER,
        service_data={ATTR_ENTITY_ID: TEST_COVER_ENTITY},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_COVER_ENTITY)
    assert state
    assert state.state == "opening"

    for _ in range(11):
        future = dt_util.utcnow() + datetime.timedelta(seconds=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

    state = hass.states.get(TEST_COVER_ENTITY)
    assert state
    assert state.state == "open"
    assert state.attributes == {
        "friendly_name": "Garage Door",
        "current_position": 100,
        "supported_features": 3,
    }

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_CLOSE_COVER,
        service_data={ATTR_ENTITY_ID: TEST_COVER_ENTITY},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_COVER_ENTITY)
    assert state
    assert state.state == "closing"

    for _ in range(11):
        future = dt_util.utcnow() + datetime.timedelta(seconds=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

    state = hass.states.get(TEST_COVER_ENTITY)
    assert state
    assert state.state == "closed"
    assert state.attributes == {
        "friendly_name": "Garage Door",
        "current_position": 0,
        "supported_features": 3,
    }



async def test_cover_positionable(hass: HomeAssistant, setup_integration: None) -> None:
    """Test cover services for a positionable cover."""

    state = hass.states.get(TEST_COVER_POSITIONABLE_ENTITY)
    assert state
    assert state.state == "closed"
    assert state.attributes == {
        "friendly_name": "Left Shade",
        "current_position": 0,
        "supported_features": 7,
    }

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_SET_COVER_POSITION,
        service_data={ATTR_ENTITY_ID: TEST_COVER_POSITIONABLE_ENTITY, ATTR_POSITION: 54},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_COVER_POSITIONABLE_ENTITY)
    assert state
    assert state.state == "opening"

    for _ in range(7):
        future = dt_util.utcnow() + datetime.timedelta(seconds=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

    state = hass.states.get(TEST_COVER_POSITIONABLE_ENTITY)
    assert state
    assert state.state == "open"
    assert state.attributes == {
        "friendly_name": "Left Shade",
        "current_position": 54,
        "supported_features": 7,
    }

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_SET_COVER_POSITION,
        service_data={ATTR_ENTITY_ID: TEST_COVER_POSITIONABLE_ENTITY, ATTR_POSITION: 22},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_COVER_POSITIONABLE_ENTITY)
    assert state
    assert state.state == "closing"

    for _ in range(5):
        future = dt_util.utcnow() + datetime.timedelta(seconds=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

    state = hass.states.get(TEST_COVER_POSITIONABLE_ENTITY)
    assert state
    assert state.state == "open"
    assert state.attributes == {
        "friendly_name": "Left Shade",
        "current_position": 22,
        "supported_features": 7,
    }
