"""Test Synthetic Home vacuum."""

import pytest


from homeassistant.const import Platform
from homeassistant.components.vacuum import (
    DOMAIN as VACUUM_DOMAIN,
    SERVICE_START,
    SERVICE_PAUSE,
    SERVICE_STOP,
    SERVICE_RETURN_TO_BASE,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .conftest import HOMES


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.VACUUM]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{HOMES}/vacuum-example.yaml", "vacuum.robot_vacuum")],
)
async def test_vacuum(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test robot vacuum."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "docked"
    assert state.attributes == {
        "friendly_name": "Robot Vacuum",
        "supported_features": 12316,
    }

    await hass.services.async_call(
        VACUUM_DOMAIN,
        SERVICE_START,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "cleaning"

    await hass.services.async_call(
        VACUUM_DOMAIN,
        SERVICE_PAUSE,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "paused"

    await hass.services.async_call(
        VACUUM_DOMAIN,
        SERVICE_STOP,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "off"

    await hass.services.async_call(
        VACUUM_DOMAIN,
        SERVICE_RETURN_TO_BASE,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "returning"
