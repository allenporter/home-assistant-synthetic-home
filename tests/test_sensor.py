"""Test Synthetic Home sensor."""

import pytest

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM


from .conftest import FIXTURES

TEST_SENSOR_FIXTURE_FILE = f"{FIXTURES}/sensor-example.yaml"
TEST_ENTITY = "sensor.thermostat_family_room_temperature"


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up switch platform."""
    return [Platform.SENSOR]


@pytest.fixture(name="us_units")
def mock_set_units(hass: HomeAssistant) -> None:
    """Fixture to set US units."""
    hass.config.units = US_CUSTOMARY_SYSTEM


@pytest.mark.parametrize(("config_yaml_fixture"), [(f"{FIXTURES}/hvac-example.yaml")])
async def test_hvac_sensors(hass: HomeAssistant, setup_integration: None) -> None:
    """Test the sensors created for an HVAC device."""

    state = hass.states.get("sensor.family_room_temperature")
    assert state
    assert state.state == "20"
    assert state.attributes == {
        "friendly_name": "Family Room Temperature",
        "device_class": "temperature",
        "state_class": "measurement",
        "unit_of_measurement": "°C",
    }

    state = hass.states.get("sensor.family_room_humidity")
    assert state
    assert state.state == "45"
    assert state.attributes == {
        "friendly_name": "Family Room Humidity",
        "device_class": "humidity",
        "state_class": "measurement",
        "unit_of_measurement": "%",
    }


@pytest.mark.parametrize(("config_yaml_fixture"), [(f"{FIXTURES}/hvac-example.yaml")])
async def test_hvac_us_units(hass: HomeAssistant, us_units: None, setup_integration: None) -> None:
    """Test the sensors created for an HVAC device."""

    state = hass.states.get("sensor.family_room_temperature")
    assert state
    assert state.state == "68"
    assert state.attributes == {
        "friendly_name": "Family Room Temperature",
        "device_class": "temperature",
        "state_class": "measurement",
        "unit_of_measurement": "°F",
    }

    state = hass.states.get("sensor.family_room_humidity")
    assert state
    assert state.state == "45"
    assert state.attributes == {
        "friendly_name": "Family Room Humidity",
        "device_class": "humidity",
        "state_class": "measurement",
        "unit_of_measurement": "%",
    }


@pytest.mark.parametrize(
    ("config_yaml_fixture"), [(f"{FIXTURES}/smart-plug-example.yaml")]
)
async def test_smart_plug(hass: HomeAssistant, setup_integration: None) -> None:
    """Test the sensors created for a smart plug."""

    state = hass.states.get("sensor.floor_lamp_energy")
    assert state
    assert state.state == "1"
    assert state.attributes == {
        "friendly_name": "Floor Lamp Energy",
        "device_class": "energy",
        "state_class": "total_increasing",
        "unit_of_measurement": "kWh",
    }


@pytest.mark.parametrize(
    ("config_yaml_fixture"), [(f"{FIXTURES}/smart-lock-example.yaml")]
)
async def test_smart_lock(hass: HomeAssistant, setup_integration: None) -> None:
    """Test the sensors created for a smart lock."""
    state = hass.states.get("sensor.front_door_lock_battery")
    assert state
    assert state.state == "90"
    assert state.attributes == {
        "friendly_name": "Front Door Lock Battery",
        "device_class": "battery",
        "state_class": "measurement",
        "unit_of_measurement": "%",
    }
