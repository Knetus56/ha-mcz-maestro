"""Button pour MCZ Maestro (reboot ESP1+ESP2 — ne touche pas le poêle)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CMD_REBOOT, CONF_TOPIC_PREFIX, DOMAIN, TOPIC_ONLINE
from .entity import MczEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the reboot button from a config entry."""
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_TOPIC_PREFIX]
    async_add_entities([MczRebootButton(entry, prefix)])


class MczRebootButton(MczEntity, ButtonEntity):
    """Redémarre ESP1+ESP2 via `Set/reboot` (pas d'action sur le poêle)."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry: ConfigEntry, prefix: str) -> None:
        super().__init__(entry, "reboot", "reboot")
        self._prefix = prefix
        self._attr_available = False
        self._unsub_online: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        @callback
        def _online(msg: Any) -> None:
            self._attr_available = msg.payload == "1"
            self.async_write_ha_state()

        self._unsub_online = await mqtt.async_subscribe(
            self.hass, f"{self._prefix}/{TOPIC_ONLINE}", _online
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_online:
            self._unsub_online()

    async def async_press(self) -> None:
        await mqtt.async_publish(self.hass, f"{self._prefix}/{CMD_REBOOT}", "1")
