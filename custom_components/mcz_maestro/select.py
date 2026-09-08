"""Selects for MCZ Maestro (fan, sortie — 0-5 ou "A" pour le mode auto)."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CMD_FAN,
    CMD_SORTIE,
    CONF_TOPIC_PREFIX,
    DOMAIN,
    FAN_SORTIE_AUTO_LABEL,
    FAN_SORTIE_AUTO_RAW,
    FAN_SORTIE_OPTIONS,
    TOPIC_FAN,
    TOPIC_SORTIE,
)
from .entity import MczMqttEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MCZ Maestro selects from a config entry."""
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_TOPIC_PREFIX]
    async_add_entities(
        [
            MczFanSortieSelect(entry, "fan", "fan", prefix, TOPIC_FAN, CMD_FAN),
            MczFanSortieSelect(entry, "sortie", "sortie", prefix, TOPIC_SORTIE, CMD_SORTIE),
        ]
    )


class MczFanSortieSelect(MczMqttEntity, SelectEntity):
    """fan et sortie partagent le même encodage : 0-5 direct, 6 = "A"."""

    _attr_options = FAN_SORTIE_OPTIONS

    def __init__(
        self,
        entry: ConfigEntry,
        key: str,
        translation_key: str,
        prefix: str,
        state_suffix: str,
        cmd_suffix: str,
    ) -> None:
        super().__init__(entry, key, translation_key, prefix, state_suffix)
        self._cmd_suffix = cmd_suffix

    def _handle_state(self, payload: str) -> None:
        self._attr_current_option = (
            FAN_SORTIE_AUTO_LABEL if payload == FAN_SORTIE_AUTO_RAW else payload
        )

    async def async_select_option(self, option: str) -> None:
        raw = FAN_SORTIE_AUTO_RAW if option == FAN_SORTIE_AUTO_LABEL else option
        await self._async_publish(self._cmd_suffix, raw)
