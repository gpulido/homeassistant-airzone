import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries, core
from homeassistant.const import CONF_DEVICE_CLASS, CONF_DEVICE_ID, CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import (
    CONF_SPEED_PERCENTAGE,
    DEFAULT_DEVICE_CLASS,
    DEFAULT_DEVICE_ID,
    DEFAULT_SPEED_AS_PER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

AIRZONE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=7000): vol.Coerce(int),
        vol.Optional(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): int,
        vol.Optional(CONF_DEVICE_CLASS, default=DEFAULT_DEVICE_CLASS): vol.In(["innobus", "aido"]),
        vol.Optional(CONF_SPEED_PERCENTAGE, default=DEFAULT_SPEED_AS_PER): cv.boolean        

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
            aido_args = {"speed_as_per": user_input[CONF_SPEED_PERCENTAGE]}    
            try:
                airzone_factory(host, port, machine_id, system_class, **aido_args)
            except:
                errors["base"] = "connection"
            if not errors:
                self.data = user_input

                return self.async_create_entry(title="Airzone", data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=AIRZONE_SCHEMA, errors=errors
        )
