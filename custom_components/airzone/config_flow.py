import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries, core
from homeassistant.const import CONF_DEVICE_CLASS, CONF_DEVICE_ID, CONF_HOST, CONF_PORT, CONF_PASSWORD, CONF_EMAIL, \
    CONF_ENTITY_ID, CONF_ID
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import (
    CONF_SPEED_PERCENTAGE,
    DEFAULT_DEVICE_CLASS,
    DEFAULT_DEVICE_ID,
    DEFAULT_SPEED_AS_PER,
    DOMAIN,
    SYSTEM_TYPES,
)

_LOGGER = logging.getLogger(__name__)

AIRZONE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=7000): vol.Coerce(int),
        vol.Optional(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): int,
        vol.Optional(CONF_SPEED_PERCENTAGE, default=DEFAULT_SPEED_AS_PER): cv.boolean
    }
)

CLOUD_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_ENTITY_ID, default=DEFAULT_DEVICE_ID): int,
        vol.Optional(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): int,
        vol.Optional(CONF_ID, default=DEFAULT_DEVICE_ID): int,
    }
)

TYPE_SELECTOR = vol.Schema(
    {
        vol.Optional(CONF_DEVICE_CLASS, default=DEFAULT_DEVICE_CLASS): vol.In(SYSTEM_TYPES),
    }
)


class AirzoneConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        if user_input is not None:
            input = user_input[CONF_DEVICE_CLASS]
            if input == "airzone_cloud":
                return await self.async_step_cloud(None)
            else:
                return await self.async_step_local(None, input)

        return self.async_show_form(step_id="user", data_schema=TYPE_SELECTOR, errors={})

    async def async_step_local(self, user_input: Optional[Dict[str, Any]] = None, system_class: str = "innobus"):
        errors: Dict[str, str] = {}
        if user_input is not None:
            port = user_input[CONF_PORT]
            host = user_input[CONF_HOST]
            machine_id = user_input[CONF_DEVICE_ID]
            aidoo_args = {"speed_as_per": user_input[CONF_SPEED_PERCENTAGE]}
            try:
                from .climate import airzone_factory
                m = await self.hass.async_add_executor_job(lambda: airzone_factory(host, port, machine_id, system_class, **aidoo_args))
                if not m.machine_state:
                    errors["base"] = "connection"
            except Exception as e:
                _LOGGER.error(e)
                errors["base"] = "connection"
            if not errors:
                self.data = user_input
                return self.async_create_entry(title="Airzone", data=self.data)

        return self.async_show_form(step_id="local", data_schema=AIRZONE_SCHEMA, errors=errors)

    async def async_step_cloud(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]
            args = {"installation": user_input[CONF_ENTITY_ID], "group": user_input[CONF_ID], "device": user_input[CONF_DEVICE_ID]}
            user_input[CONF_DEVICE_CLASS] = "airzone_cloud"
            try:
                from .climate import generate_airzone_cloud
                m = await self.hass.async_add_executor_job(lambda: generate_airzone_cloud(email, password, **args))
                if not m.machine_state:
                    errors["base"] = "connection"
            except Exception as e:
                _LOGGER.error(e)
                errors["base"] = "connection"
            if not errors:
                self.data = user_input
                return self.async_create_entry(title="Airzone", data=self.data)

        return self.async_show_form(step_id="cloud", data_schema=CLOUD_SCHEMA, errors=errors)
