"""Global fixtures for Synthetic Home integration."""

import pathlib
from collections.abc import Generator
from unittest.mock import patch, mock_open

import pytest


from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from syrupy.extensions.amber import AmberSnapshotExtension
from syrupy.location import PyTestLocation

DIFFERENT_DIRECTORY = "__snaps_example__"
from custom_components.synthetic_home.const import (
    DOMAIN,
    CONF_FILENAME,
    ATTR_AREA_NAME,
    ATTR_RESTORABLE_ATTRIBUTES_KEY,
    ATTR_DEVICE_NAME,
    ATTR_CONFIG_ENTRY_ID,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry

TEST_FILENAME = "example.yaml"
FIXTURES = "tests/fixtures"

DIFFERENT_DIRECTORY = "snapshots"


class DifferentDirectoryExtension(AmberSnapshotExtension):
    @classmethod
    def dirname(cls, *, test_location: "PyTestLocation") -> str:
        return str(
            pathlib.Path(test_location.filepath).parent.joinpath(DIFFERENT_DIRECTORY)
        )


@pytest.fixture
def snapshot(snapshot):
    return snapshot.use_extension(DifferentDirectoryExtension)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None, None, None]:
    """Enable custom integration."""
    _ = enable_custom_integrations  # unused
    yield


@pytest.fixture(name="config_entry")
def mock_config_entry() -> MockConfigEntry:
    """Fixture for mock configuration entry."""
    return MockConfigEntry(domain=DOMAIN, data={CONF_FILENAME: TEST_FILENAME})


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Fixture for platforms loaded by the integration."""
    return []


@pytest.fixture(name="setup_integration")
async def mock_setup_integration(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    platforms: list[Platform],
) -> None:
    """Set up the integration."""
    config_entry.add_to_hass(hass)
    with patch("custom_components.synthetic_home.PLATFORMS", platforms):
        assert await async_setup_component(hass, DOMAIN, {})
        await hass.async_block_till_done()
        yield


@pytest.fixture(name="config_yaml_fixture")
def mock_config_yaml_fixture() -> str | None:
    """Mock out the yaml config file contents."""
    return None


@pytest.fixture(name="config_yaml")
def mock_config_yaml(config_yaml_fixture: str | None) -> str:
    """Mock out the yaml config file contents."""
    if config_yaml_fixture:
        with pathlib.Path(config_yaml_fixture).open("r") as f:
            return f.read()
    return ""


@pytest.fixture(autouse=True)
def mock_config_content(config_yaml: str) -> None:
    """Mock out the yaml config file contents."""
    with patch(
        "custom_components.synthetic_home.home_model.synthetic_home.read_config_content",
        mock_open(read_data=config_yaml),
    ):
        yield


async def restore_state(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    area_name: str,
    device_name: str,
    restorable_attributes_key: str,
) -> None:
    """Restore the specified pre-canned state."""
    await hass.services.async_call(
        DOMAIN,
        "set_synthetic_device_state",
        service_data={
            ATTR_CONFIG_ENTRY_ID: config_entry.entry_id,
            ATTR_DEVICE_NAME: device_name,
            ATTR_AREA_NAME: area_name,
            ATTR_RESTORABLE_ATTRIBUTES_KEY: restorable_attributes_key,
        },
        blocking=True,
    )
    await hass.async_block_till_done()


async def clear_restore_state(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Clear any previous restore state."""
    await hass.services.async_call(
        DOMAIN,
        "clear_synthetic_device_state",
        service_data={
            ATTR_CONFIG_ENTRY_ID: config_entry.entry_id,
        },
        blocking=True,
    )
    await hass.async_block_till_done()
