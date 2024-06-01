"""Test Synthetic Home lock."""

import pytest
from syrupy import SnapshotAssertion

from homeassistant.const import Platform
from homeassistant.components.lock import (
    SERVICE_LOCK,
    SERVICE_UNLOCK,
    DOMAIN as LOCK_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import FIXTURES, restore_state


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up switch platform."""
    return [Platform.LOCK]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/smart-lock-example.yaml", "lock.front_door_lock")],
)
async def test_smart_lock(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test a binary sensors for a smart lock."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "locked"
    assert state.attributes == {
        "friendly_name": "Front Door Lock",
        "supported_features": 0,
    }

    await hass.services.async_call(
        LOCK_DOMAIN,
        SERVICE_UNLOCK,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "unlocked"

    await hass.services.async_call(
        LOCK_DOMAIN,
        SERVICE_LOCK,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "locked"


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/smart-lock-example.yaml", "lock.front_door_lock")],
)
@pytest.mark.parametrize(
    ("device_state"),
    [("locked"), ("unlocked")],
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

    await restore_state(
        hass, config_entry, "Front door", "Front Door Lock", device_state
    )
    state = hass.states.get(test_entity)
    assert state
    assert (state.state, state.attributes) == snapshot
