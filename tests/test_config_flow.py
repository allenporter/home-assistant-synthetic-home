"""Test Synthetic Home config flow."""
from unittest.mock import patch

import pytest

from custom_components.synthetic_home.const import (
    DOMAIN,
)
from homeassistant import config_entries
from homeassistant import data_entry_flow


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with patch(
        "custom_components.synthetic_home.async_setup_entry",
        return_value=True,
    ):
        yield



async def test_successful_config_flow(hass):
    """Test a successful config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "Synthetic Home"
    assert result["data"] == {}
    assert result["result"]
