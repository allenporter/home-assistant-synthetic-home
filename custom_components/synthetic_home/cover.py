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
    CoverEntityDescription,
    DOMAIN as COVER_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN
from .entity import SyntheticDeviceEntity
from .model import ParsedDevice

COVER_STEP = 10
COVER_STEP_TIME = datetime.timedelta(seconds=1)


class SyntheticCoverEntityDescription(CoverEntityDescription, frozen_or_thawed=True):
    """Entity description for a cover entity."""

    supported_features: CoverEntityFeature | None = None


COVERS: tuple[SyntheticCoverEntityDescription, ...] = (
    SyntheticCoverEntityDescription(
        key="blinds-cover",
        supported_features=CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION,
        device_class=CoverDeviceClass.BLIND,
    ),
    SyntheticCoverEntityDescription(
        key="garage-door-cover",
        device_class=CoverDeviceClass.GARAGE,
        supported_features=CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE,
    ),
    SyntheticCoverEntityDescription(
        key="gate-cover",
        device_class=CoverDeviceClass.GATE,
        supported_features=CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE,
    ),
)
COVER_MAP = {desc.key: desc for desc in COVERS}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up light platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticCover(device, COVER_MAP[entity.entity_key], **entity.attributes)
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
    _attr_current_cover_position = 0

    _target_cover_position: int | None = None
    _timer_unsub: CALLBACK_TYPE | None = None

    def __init__(
        self,
        device: ParsedDevice,
        entity_desc: SyntheticCoverEntityDescription,
    ) -> None:
        """Initialize the SyntheticCover."""
        super().__init__(device, entity_desc.key)
        self.entity_description = entity_desc
        self._attr_supported_features = entity_desc.supported_features

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
        if self._attr_current_cover_position > self._target_cover_position:
            self._attr_current_cover_position -= COVER_STEP
            self._attr_current_cover_position = max(
                self._attr_current_cover_position, self._target_cover_position
            )
        elif self._attr_current_cover_position < self._target_cover_position:
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
