"""Cover platform for Synthetic Home."""

import datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback, CALLBACK_TYPE
from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
    ATTR_POSITION,
    DOMAIN as COVER_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN
from .entity import SyntheticDeviceEntity
from .model import ParsedDevice

COVER_STEP = 10
COVER_STEP_TIME = datetime.timedelta(seconds=1)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up cover platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticCover(device, entity.entity_key, **entity.attributes)
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == COVER_DOMAIN
    )


class SyntheticCover(SyntheticDeviceEntity, CoverEntity):
    """synthetic_home cover class."""

    # These are the attributes that represent the cover state
    _attr_is_closing = False
    _attr_is_closed = True
    _attr_is_opening = False
    # The position is used to infer the other attributes (0 is closed, 100 is open)
    _attr_current_cover_position: int = 0

    _target_cover_position: int | None = None
    _timer_unsub: CALLBACK_TYPE | None = None

    def __init__(
        self,
        device: ParsedDevice,
        key: str,
        supported_features: CoverEntityFeature,
        *,
        device_class: CoverDeviceClass | None = None,
        state: bool | None = None,
    ) -> None:
        """Initialize the SyntheticCover."""
        super().__init__(device, key)
        self._attr_supported_features = supported_features
        if device_class:
            self._attr_device_class = device_class
        if state:
            self._attr_current_cover_position = 100

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from Home Assistant."""
        if self._timer_unsub is not None:
            self._timer_unsub()
            self._timer_unsub = None

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        if self._attr_current_cover_position == 0:
            # Already closed
            return
        self._attr_is_closing = True
        self._attr_is_opening = False
        self._target_cover_position = 0
        self._start_moving()
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""

        if self._attr_current_cover_position == 1000:
            # Already open
            return

        # The following attributes are set
        self._attr_is_closing = False
        self._attr_is_opening = True
        self._target_cover_position = 100
        self._start_moving()
        self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        position: int = kwargs[ATTR_POSITION]
        if self._attr_current_cover_position == position:
            # Nothing to do
            return
        self._target_cover_position = position
        self._attr_is_closing = (
            self._target_cover_position < self._attr_current_cover_position
        )
        self._attr_is_opening = (
            self._target_cover_position > self._attr_current_cover_position
        )
        self._start_moving()
        self.async_write_ha_state()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        self._is_closing = False
        self._is_opening = False
        if self._timer_unsub is not None:
            self._timer_unsub()
            self._timer_unsub = None
            self._target_cover_position = None

    @callback
    def _start_moving(self) -> None:
        """Start moving the cover."""
        if self._timer_unsub is None:
            self._timer_unsub = async_track_time_interval(
                self.hass,
                action=self._move_cover,
                interval=COVER_STEP_TIME,
            )

    async def _move_cover(self, now: datetime.datetime) -> None:
        """Track time changes."""
        if (
            self._target_cover_position is not None
            and self._attr_current_cover_position > self._target_cover_position
        ):
            self._attr_current_cover_position -= COVER_STEP
            self._attr_current_cover_position = max(
                self._attr_current_cover_position, self._target_cover_position
            )
        elif (
            self._target_cover_position is not None
            and self._attr_current_cover_position < self._target_cover_position
        ):
            self._attr_current_cover_position += COVER_STEP
            self._attr_current_cover_position = min(
                self._attr_current_cover_position, self._target_cover_position
            )
        else:
            # Reached target
            self._attr_is_closing = False
            self._attr_is_opening = False
            self._attr_is_closed = self._attr_current_cover_position == 0
            await self.async_stop_cover()
        self.async_write_ha_state()
