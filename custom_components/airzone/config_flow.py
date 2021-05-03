import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries, core
from homeassistant.const import CONF_DEVICE_CLASS, CONF_DEVICE_ID, CONF_HOST, CONF_PORT
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get_registry,
)
import voluptuous as vol

from .const import DEFAULT_DEVICE_CLASS, DEFAULT_DEVICE_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

AIRZONE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=7000): vol.Coerce(int),
        vol.Optional(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): int,
        vol.Optional(CONF_DEVICE_CLASS, default=DEFAULT_DEVICE_CLASS): vol.In(["innobus", "aido"])
    }
)

class AirzoneConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Github Custom config flow."""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:

            from airzone import airzone_factory
            port = user_input[CONF_PORT]
            host = user_input[CONF_HOST]
            machine_id = user_input[CONF_DEVICE_ID]
            system_class = user_input[CONF_DEVICE_CLASS]
            try:
                machine = airzone_factory(host, port, machine_id, system_class)
            except:
                errors["base"] = "connection"
            if not errors:
                self.data = user_input

                return self.async_create_entry(title="Airzone", data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=AIRZONE_SCHEMA, errors=errors
        )
