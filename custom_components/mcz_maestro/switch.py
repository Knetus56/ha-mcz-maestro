"""Switches for MCZ Maestro.

on_off / control_mode / son sont de vrais topics firmware.
demarrage_automatique est une entité locale pure (pas de topic, cf.
PLUGIN_NOTES.md ⚠️ : créée manuellement par l'utilisateur pour ses propres
automatisations, à réintégrer telle quelle côté plugin).
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CMD_CONTROL_MODE,
    CMD_ON_OFF,
    CMD_SON,
    CONF_TOPIC_PREFIX,
    DOMAIN,
    ON_OFF_OFF,
    ON_OFF_ON,
    TOPIC_CONTROL_MODE,
    TOPIC_ON_OFF,
    TOPIC_SON,
)
from .entity import MczLocalEntity, MczMqttEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MCZ Maestro switches from a config entry."""
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_TOPIC_PREFIX]
    async_add_entities(
        [
            MczOnOffSwitch(entry, "on_off", "on_off", prefix, TOPIC_ON_OFF),
            MczControlModeSwitch(
                entry, "control_mode", "control_mode", prefix, TOPIC_CONTROL_MODE
            ),
            MczSonSwitch(entry, "son", "son", prefix, TOPIC_SON),
            MczDemarrageAutomatiqueSwitch(entry, "demarrage_automatique", "demarrage_automatique"),
        ]
    )


class MczOnOffSwitch(MczMqttEntity, SwitchEntity):
    """Marche/arrêt du poêle (valeurs magiques du protocole, cf. const.py)."""

    def _handle_state(self, payload: str) -> None:
        self._attr_is_on = payload == "1"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_publish(CMD_ON_OFF, ON_OFF_ON)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_publish(CMD_ON_OFF, ON_OFF_OFF)


class MczControlModeSwitch(MczMqttEntity, SwitchEntity):
    """control_mode (entier côté firmware, exposé en switch on/off)."""

    def _handle_state(self, payload: str) -> None:
        self._attr_is_on = payload not in ("0", "")

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_publish(CMD_CONTROL_MODE, "1")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_publish(CMD_CONTROL_MODE, "0")


class MczSonSwitch(MczMqttEntity, SwitchEntity):
    """Bip sonore du poêle."""

    def _handle_state(self, payload: str) -> None:
        self._attr_is_on = payload == "1"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_publish(CMD_SON, "1")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_publish(CMD_SON, "0")


class MczDemarrageAutomatiqueSwitch(MczLocalEntity, RestoreEntity, SwitchEntity):
    """Helper local (pas une donnée du poêle) pour les automatisations de
    l'utilisateur — état simplement restauré au redémarrage de HA."""

    def __init__(self, entry: ConfigEntry, key: str, translation_key: str) -> None:
        RestoreEntity.__init__(self)
        MczLocalEntity.__init__(self, entry, key, translation_key)
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._attr_is_on = last_state.state == "on"

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()
