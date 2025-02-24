"""Test Synthetic Home device_tracker."""

import pytest

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant


from .conftest import FIXTURES


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.DEVICE_TRACKER]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/mobile-phone-example.yaml", "device_tracker.android")],
)
async def test_device_tracker(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test an alarm control panel device."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "home"
    assert state.attributes == {
        "friendly_name": "Android",
        "source_type": "gps",
    }
