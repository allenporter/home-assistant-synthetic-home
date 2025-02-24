"""Test Synthetic Home alarm_control_panel."""

import pytest

from homeassistant.const import Platform
from homeassistant.components.alarm_control_panel import (
    DOMAIN as ALARM_CONTROL_PANEL_DOMAIN,
    SERVICE_ALARM_ARM_AWAY,
    SERVICE_ALARM_ARM_HOME,
    SERVICE_ALARM_DISARM,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant


from .conftest import FIXTURES


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.ALARM_CONTROL_PANEL]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/alarm-system-example.yaml", "alarm_control_panel.alarm")],
)
async def test_alarm_control_nale(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test an alarm control panel device."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "disarmed"
    assert state.attributes == {
        "friendly_name": "Alarm",
        "supported_features": 11,
        "code_format": "number",
        "code_arm_required": False,
        "changed_by": None,
    }

    await hass.services.async_call(
        ALARM_CONTROL_PANEL_DOMAIN,
        SERVICE_ALARM_ARM_HOME,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "armed_home"

    await hass.services.async_call(
        ALARM_CONTROL_PANEL_DOMAIN,
        SERVICE_ALARM_DISARM,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "disarmed"

    await hass.services.async_call(
        ALARM_CONTROL_PANEL_DOMAIN,
        SERVICE_ALARM_ARM_AWAY,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "armed_away"
