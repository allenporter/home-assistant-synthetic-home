"""Test Synthetic Home config flow."""

from unittest.mock import patch, mock_open

import pytest

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType


from custom_components.synthetic_home.const import DOMAIN, CONF_FILENAME


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
    assert result["type"] == FlowResultType.FORM
    assert not result["errors"]

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_FILENAME: "my-username",
        },
    )
    await hass.async_block_till_done()

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {CONF_FILENAME: "does_not_exist"}

    with patch(
        "custom_components.synthetic_home.config_flow.read_config",
        mock_open(read_data=""),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_FILENAME: "example.yaml",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "example.yaml"
    assert result["data"] == {CONF_FILENAME: "example.yaml"}
    assert result["result"]
