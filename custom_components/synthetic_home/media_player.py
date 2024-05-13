"""Media platform for Synthetic Home."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityDescription,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaPlayerDeviceClass,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticDeviceEntity
from .model import ParsedDevice

VOLUME_STEP = 1
SUPPORTED_FEATURES = (
    MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
)


class SyntheticMediaPlayerEntityDescription(
    MediaPlayerEntityDescription, frozen_or_thawed=True
):
    """Entity description for a media player entity."""

    supported_features: MediaPlayerEntityFeature | None = None


MEDIA_PLAYERS: tuple[SyntheticMediaPlayerEntityDescription, ...] = (
    SyntheticMediaPlayerEntityDescription(
        key="speaker",
        supported_features=SUPPORTED_FEATURES,
        device_class=MediaPlayerDeviceClass.SPEAKER,
    ),
    SyntheticMediaPlayerEntityDescription(
        key="tv",
        supported_features=SUPPORTED_FEATURES,
        device_class=MediaPlayerDeviceClass.TV,
    ),
)
MEDIA_PLAYER_MAP = {desc.key: desc for desc in MEDIA_PLAYERS}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up media player platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticMediaPlayer(
            device, MEDIA_PLAYER_MAP[entity.entity_key], **entity.attributes
        )
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == MEDIA_PLAYER_DOMAIN
    )


class SyntheticMediaPlayer(SyntheticDeviceEntity, MediaPlayerEntity):
    """synthetic_home media player class."""

    def __init__(
        self,
        device: ParsedDevice,
        entity_desc: SyntheticMediaPlayerEntityDescription,
    ) -> None:
        """Initialize the SyntheticMediaPlayer."""
        super().__init__(device, entity_desc.key)
        self._attr_state = MediaPlayerState.PLAYING
        self._attr_volume_level = 1.0
        self.entity_description = entity_desc
        if entity_desc.supported_features is not None:
            self._attr_supported_features = entity_desc.supported_features

    def turn_on(self) -> None:
        """Turn the media player on."""
        self._attr_state = MediaPlayerState.PLAYING
        self.schedule_update_ha_state()

    def turn_off(self) -> None:
        """Turn the media player off."""
        self._attr_state = MediaPlayerState.OFF
        self.schedule_update_ha_state()

    def mute_volume(self, mute: bool) -> None:
        """Mute the volume."""
        self._attr_is_volume_muted = mute
        self.schedule_update_ha_state()

    def volume_up(self) -> None:
        """Increase volume."""
        assert self.volume_level is not None
        self._attr_volume_level = min(1.0, self.volume_level + 0.1)
        self.schedule_update_ha_state()

    def volume_down(self) -> None:
        """Decrease volume."""
        assert self.volume_level is not None
        self._attr_volume_level = max(0.0, self.volume_level - 0.1)
        self.schedule_update_ha_state()

    def set_volume_level(self, volume: float) -> None:
        """Set the volume level, range 0..1."""
        self._attr_volume_level = volume
        self.schedule_update_ha_state()

    def media_play(self) -> None:
        """Send play command."""
        self._attr_state = MediaPlayerState.PLAYING
        self.schedule_update_ha_state()

    def media_pause(self) -> None:
        """Send pause command."""
        self._attr_state = MediaPlayerState.PAUSED
        self.schedule_update_ha_state()

    def media_stop(self) -> None:
        """Send stop command."""
        self._attr_state = MediaPlayerState.OFF
        self.schedule_update_ha_state()
