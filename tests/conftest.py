"""Global fixtures for Synthetic Home integration."""

from collections.abc import Generator
from unittest.mock import patch, mock_open

import pytest

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.synthetic_home.const import DOMAIN, CONF_FILENAME

from pytest_homeassistant_custom_component.common import MockConfigEntry

TEST_FILENAME = "example.yaml"


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

@pytest.fixture(name="config_yaml")
def mock_config_yaml() -> str:
    """Mock out the yaml config file contents."""


@pytest.fixture(autouse=True)
def mock_config_content(config_yaml: str) -> None:
    """Mock out the yaml config file contents."""
    with patch(
        "custom_components.synthetic_home.read_config_content",
        mock_open(read_data=config_yaml),
    ):
        yield
