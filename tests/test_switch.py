"""Test Synthetic Home switch."""

import pytest

from homeassistant.const import Platform
from homeassistant.components.switch import (
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    DOMAIN as SWITCH_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .conftest import FIXTURES

TEST_ENTITY = "switch.smart_feeder"


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up switch platform."""
    return [Platform.SWITCH]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/switch-example.yaml", "switch.smart_feeder")],
)
async def test_switch_services(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test switch services."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "on"
    assert state.attributes == {
        "friendly_name": "Smart Feeder",
        "device_class": "switch",
    }

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "off"

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "on"


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/smart-plug-example.yaml", "switch.floor_lamp")],
)
async def test_smart_plug(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test a switch for a smart plug device."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Floor Lamp",
        "device_class": "outlet",
    }

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "off"

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "on"
