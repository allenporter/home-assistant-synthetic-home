"""Global test fixtures for Synthetic Home integration."""

import pathlib
from collections.abc import Generator
from unittest.mock import patch, mock_open

import pytest
from syrupy import SnapshotAssertion
from aiohttp.test_utils import TestClient

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from syrupy.extensions.amber import AmberSnapshotExtension
from syrupy.location import PyTestLocation

from custom_components.synthetic_home.const import (
    DOMAIN,
    CONF_FILENAME,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

TEST_FILENAME = "example.yaml"
FIXTURES = "tests/fixtures"

DIFFERENT_DIRECTORY = "snapshots"


class DifferentDirectoryExtension(AmberSnapshotExtension):
    """Extension to set a different snapshot directory."""

    @classmethod
    def dirname(cls, *, test_location: "PyTestLocation") -> str:
        """Override the snapshot directory name."""
        return str(
            pathlib.Path(test_location.filepath).parent.joinpath(DIFFERENT_DIRECTORY)
        )


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion):
    """Fixture to override the snapshot directory."""
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
        assert await async_setup_component(hass, "homeassistant", {})
        await hass.config_entries.async_setup(config_entry.entry_id)
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
        "synthetic_home.inventory.read_config_content",
        mock_open(read_data=config_yaml),
    ):
        yield


@pytest.fixture
def mock_api_client(
    hass: HomeAssistant, hass_client: ClientSessionGenerator
) -> TestClient:
    """Start the Home Assistant HTTP component and return admin API client."""
    hass.loop.run_until_complete(async_setup_component(hass, "api", {}))
    return hass.loop.run_until_complete(hass_client())
