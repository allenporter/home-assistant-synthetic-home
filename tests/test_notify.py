"""Test Synthetic Home notify."""

import pytest

from homeassistant.const import Platform, ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.components.notify import (
    DOMAIN as NOTIFY_DOMAIN,
    SERVICE_SEND_MESSAGE,
)

from .conftest import FIXTURES


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.NOTIFY]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/mobile-phone-example.yaml", "notify.android")],
)
async def test_notify(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test an notify entity."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "unknown"
    assert state.attributes == {
        "friendly_name": "Android",
        "supported_features": 0,
    }

    await hass.services.async_call(
        NOTIFY_DOMAIN,
        SERVICE_SEND_MESSAGE,
        service_data={ATTR_ENTITY_ID: test_entity, "message": "Hello"},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state != "unknown"
    assert state.attributes == {
        "friendly_name": "Android",
        "supported_features": 0,
        "last_sent_message": {
            "message": "Hello",
            "title": None,
        },
    }
