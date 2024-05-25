"""Test Synthetic Home fan."""

import pytest
from syrupy import SnapshotAssertion

from homeassistant.const import Platform
from homeassistant.components.fan import (
    DOMAIN as FAN_DOMAIN,
    SERVICE_OSCILLATE,
    ATTR_OSCILLATING,
)
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON, SERVICE_TURN_OFF
from homeassistant.core import HomeAssistant

from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import FIXTURES, restore_state


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.FAN]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/fan-example.yaml", "fan.counter_fan")],
)
async def test_fan(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test fan."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Counter Fan",
        "supported_features": 3,
        "oscillating": False,
        "percentage": 0,
        "percentage_step": 1.0,
        "preset_mode": None,
        "preset_modes": None,
    }

    await hass.services.async_call(
        FAN_DOMAIN,
        SERVICE_TURN_ON,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "on"

    await hass.services.async_call(
        FAN_DOMAIN,
        SERVICE_OSCILLATE,
        service_data={ATTR_ENTITY_ID: test_entity, ATTR_OSCILLATING: True},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "on"
    assert state.attributes.get("oscillating")

    await hass.services.async_call(
        FAN_DOMAIN,
        SERVICE_OSCILLATE,
        service_data={ATTR_ENTITY_ID: test_entity, ATTR_OSCILLATING: False},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "on"
    assert not state.attributes.get("oscillating")

    await hass.services.async_call(
        FAN_DOMAIN,
        SERVICE_TURN_OFF,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "off"


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/fan-example.yaml", "fan.counter_fan")],
)
@pytest.mark.parametrize(
    ("device_state"),
    [
        "off",
        "on",
        "oscillating",
    ],
)
async def test_fan_device_state(
    hass: HomeAssistant,
    setup_integration: None,
    config_entry: MockConfigEntry,
    test_entity: str,
    device_state: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test a fan with restorable state."""

    await restore_state(hass, config_entry, "Kitchen", "Counter Fan", device_state)
    state = hass.states.get(test_entity)
    assert state
    assert (state.state, state.attributes) == snapshot
