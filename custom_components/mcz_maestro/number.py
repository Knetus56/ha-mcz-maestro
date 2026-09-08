"""Numbers for MCZ Maestro.

puissance / temperature_consigne sont de vrais topics firmware.
temperature_minimum est une entité locale pure (pas de topic, cf.
PLUGIN_NOTES.md ⚠️ : créée manuellement par l'utilisateur pour ses propres
automatisations, à réintégrer telle quelle côté plugin).
"""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode, RestoreNumber
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CMD_PUISSANCE,
    CMD_TEMPERATURE_CONSIGNE,
    CONF_TOPIC_PREFIX,
    DOMAIN,
    TEMPERATURE_MINIMUM_DEFAULT,
    TEMPERATURE_MINIMUM_MAX,
    TEMPERATURE_MINIMUM_MIN,
    TEMPERATURE_MINIMUM_STEP,
    TOPIC_PUISSANCE,
    TOPIC_TEMPERATURE_CONSIGNE,
)
from .entity import MczLocalEntity, MczMqttEntity

CONSIGNE_MIN = 15.0
CONSIGNE_MAX = 30.0
CONSIGNE_STEP = 0.5


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MCZ Maestro numbers from a config entry."""
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_TOPIC_PREFIX]
    async_add_entities(
        [
            MczPuissanceNumber(entry, "puissance", "puissance", prefix, TOPIC_PUISSANCE),
            MczTemperatureConsigneNumber(
                entry,
                "temperature_consigne",
                "temperature_consigne",
                prefix,
                TOPIC_TEMPERATURE_CONSIGNE,
            ),
            MczTemperatureMinimumNumber(entry, "temperature_minimum", "temperature_minimum"),
        ]
    )


class MczPuissanceNumber(MczMqttEntity, NumberEntity):
    """Niveau de puissance du poêle (1-5)."""

    _attr_native_min_value = 1
    _attr_native_max_value = 5
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def _handle_state(self, payload: str) -> None:
        try:
            self._attr_native_value = float(payload)
        except ValueError:
            return

    async def async_set_native_value(self, value: float) -> None:
        await self._async_publish(CMD_PUISSANCE, str(int(value)))


class MczTemperatureConsigneNumber(MczMqttEntity, NumberEntity):
    """Température de consigne (redondante avec le climate, cf. notes)."""

    _attr_native_min_value = CONSIGNE_MIN
    _attr_native_max_value = CONSIGNE_MAX
    _attr_native_step = CONSIGNE_STEP
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.BOX

    def _handle_state(self, payload: str) -> None:
        try:
            self._attr_native_value = float(payload)
        except ValueError:
            return

    async def async_set_native_value(self, value: float) -> None:
        await self._async_publish(CMD_TEMPERATURE_CONSIGNE, str(value))


class MczTemperatureMinimumNumber(MczLocalEntity, RestoreNumber):
    """Helper local (pas une donnée du poêle) pour les automatisations de
    l'utilisateur — valeur simplement restaurée au redémarrage de HA."""

    _attr_native_min_value = TEMPERATURE_MINIMUM_MIN
    _attr_native_max_value = TEMPERATURE_MINIMUM_MAX
    _attr_native_step = TEMPERATURE_MINIMUM_STEP
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.BOX

    def __init__(self, entry: ConfigEntry, key: str, translation_key: str) -> None:
        RestoreNumber.__init__(self)
        MczLocalEntity.__init__(self, entry, key, translation_key)
        self._attr_native_value = TEMPERATURE_MINIMUM_DEFAULT

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_data = await self.async_get_last_number_data()
        if last_data is not None and last_data.native_value is not None:
            self._attr_native_value = last_data.native_value

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()
