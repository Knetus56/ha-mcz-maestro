"""Config flow for the MCZ Maestro integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_TOPIC_PREFIX, DEFAULT_NAME, DEFAULT_TOPIC_PREFIX, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_TOPIC_PREFIX, default=DEFAULT_TOPIC_PREFIX): str,
    }
)


class MczMaestroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MCZ Maestro (instance unique : un seul poêle)."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial (and only) step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            topic_prefix = user_input[CONF_TOPIC_PREFIX].strip().rstrip("/")

            if not topic_prefix:
                errors[CONF_TOPIC_PREFIX] = "invalid_topic_prefix"
            else:
                # Un seul poêle géré par cette intégration : une instance
                # par préfixe de topic (permet quand même plusieurs poêles
                # si jamais besoin un jour, sans jamais dupliquer par erreur
                # la même config).
                await self.async_set_unique_id(topic_prefix)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_TOPIC_PREFIX: topic_prefix,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
