"""Alarm control panel platform for Synthetic Home."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    DOMAIN as ALARM_CONTROL_PANEL_DOMAIN,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
    CodeFormat,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes

_LOGGER = logging.getLogger(__name__)

SUPPORTED_ATTRIBUTES = set(
    {
        "code_format",
        "supported_features",
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up alarm_control_pael platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeAlarmControlPanel(
            entity,
            state=entity.state,
            **filter_attributes(entity, SUPPORTED_ATTRIBUTES),
        )
        for entity in synthetic_home.entities
        if entity.platform == ALARM_CONTROL_PANEL_DOMAIN
    )


class SyntheticHomeAlarmControlPanel(SyntheticEntity, AlarmControlPanelEntity):
    """synthetic_home switch class."""

    def __init__(
        self,
        entity: ParsedEntity,
        state: AlarmControlPanelState | None = None,
        *,
        code_format: CodeFormat | None = None,
        supported_features: AlarmControlPanelEntityFeature | None = None,
    ) -> None:
        """Initialize SyntheticHomeBinarySwitch."""
        super().__init__(entity)
        _LOGGER.info("state=%s", state)
        if state is not None:
            self._attr_alarm_state = state
        if code_format is not None:
            self._attr_code_format = code_format
        if supported_features is not None:
            self._attr_supported_features = (
                AlarmControlPanelEntityFeature(0) | supported_features
            )
        self._attr_code_arm_required = False

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        self._attr_alarm_state = AlarmControlPanelState.DISARMED
        self.async_write_ha_state()

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        self._attr_alarm_state = AlarmControlPanelState.ARMED_HOME
        self.async_write_ha_state()

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        self._attr_alarm_state = AlarmControlPanelState.ARMED_AWAY
        self.async_write_ha_state()

    async def async_alarm_arm_night(self, code: str | None = None) -> None:
        """Send arm night command."""
        self._attr_alarm_state = AlarmControlPanelState.ARMED_NIGHT
        self.async_write_ha_state()

    async def async_alarm_arm_vacation(self, code: str | None = None) -> None:
        """Send arm vacation command."""
        self._attr_alarm_state = AlarmControlPanelState.ARMED_VACATION
        self.async_write_ha_state()

    async def async_alarm_trigger(self, code: str | None = None) -> None:
        """Send alarm trigger command."""
        self._attr_alarm_state = AlarmControlPanelState.TRIGGERED
        self.async_write_ha_state()
