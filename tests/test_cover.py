"""Test Synthetic Home cover."""

import datetime

import pytest
from syrupy import SnapshotAssertion

from homeassistant.const import Platform
from homeassistant.components.cover import (
    DOMAIN as COVER_DOMAIN,
    SERVICE_OPEN_COVER,
    SERVICE_CLOSE_COVER,
    SERVICE_SET_COVER_POSITION,
    ATTR_POSITION,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import FIXTURES, restore_state


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.COVER]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/smart-blinds-example.yaml", "cover.left_shade")],
)
async def test_smart_blinds(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test smart blinds which are a positionable cover."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "closed"
    assert state.attributes == {
        "friendly_name": "Left Shade",
        "device_class": "blind",
        "current_position": 0,
        "supported_features": 7,
    }

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_SET_COVER_POSITION,
        service_data={ATTR_ENTITY_ID: test_entity, ATTR_POSITION: 54},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "opening"

    for _ in range(7):
        future = dt_util.utcnow() + datetime.timedelta(seconds=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "open"
    assert state.attributes == {
        "friendly_name": "Left Shade",
        "device_class": "blind",
        "current_position": 54,
        "supported_features": 7,
    }

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_SET_COVER_POSITION,
        service_data={ATTR_ENTITY_ID: test_entity, ATTR_POSITION: 22},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "closing"

    for _ in range(5):
        future = dt_util.utcnow() + datetime.timedelta(seconds=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "open"
    assert state.attributes == {
        "friendly_name": "Left Shade",
        "device_class": "blind",
        "current_position": 22,
        "supported_features": 7,
    }


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/garage-door-example.yaml", "cover.garage_door")],
)
async def test_garage_door(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test a garage door device."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "closed"
    assert state.attributes == {
        "friendly_name": "Garage Door",
        "device_class": "garage",
        "current_position": 0,
        "supported_features": 3,
    }

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_OPEN_COVER,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "opening"

    for _ in range(11):
        future = dt_util.utcnow() + datetime.timedelta(seconds=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "open"
    assert state.attributes == {
        "friendly_name": "Garage Door",
        "device_class": "garage",
        "current_position": 100,
        "supported_features": 3,
    }

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_CLOSE_COVER,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "closing"

    for _ in range(11):
        future = dt_util.utcnow() + datetime.timedelta(seconds=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "closed"
    assert state.attributes == {
        "friendly_name": "Garage Door",
        "device_class": "garage",
        "current_position": 0,
        "supported_features": 3,
    }


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/gate-example.yaml", "cover.driveway_gate")],
)
async def test_gate(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test a gate device as a cover entity."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "closed"
    assert state.attributes == {
        "friendly_name": "Driveway Gate",
        "device_class": "gate",
        "current_position": 0,
        "supported_features": 3,
    }


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/smart-blinds-example.yaml", "cover.left_shade")],
)
@pytest.mark.parametrize(
    ("device_state"),
    [
        (device_state)
        for device_state in ("open", "closed")
    ],
)
async def test_hvac_device_state(
    hass: HomeAssistant,
    setup_integration: None,
    test_entity: str,
    device_state: str,
    config_entry: MockConfigEntry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test an HVAC device with restorable state."""

    await restore_state(hass, config_entry, "Family Room", "Left Shade", device_state)
    state = hass.states.get(test_entity)
    assert state
    assert (state.state, state.attributes) == snapshot
