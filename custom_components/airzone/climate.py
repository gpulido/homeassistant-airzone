from datetime import timedelta
import logging
from typing import Callable, Optional

from airzone import airzone_factory
from homeassistant import config_entries, core
from homeassistant.components.climate import PLATFORM_SCHEMA
from homeassistant.const import CONF_DEVICE_CLASS, CONF_DEVICE_ID, CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .const import (
    CONF_SPEED_PERCENTAGE,
    DEFAULT_DEVICE_CLASS,
    DEFAULT_DEVICE_ID,
    DEFAULT_SPEED_AS_PER,
    DOMAIN,
    SYSTEM_TYPES,
)

SCAN_INTERVAL = timedelta(seconds=10)

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Optional(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): int,
        vol.Optional(CONF_DEVICE_CLASS, default=DEFAULT_DEVICE_CLASS): vol.In(SYSTEM_TYPES),
        vol.Optional(CONF_SPEED_PERCENTAGE, default=DEFAULT_SPEED_AS_PER): cv.boolean        
    }
)

def get_devices(config):
    port = config[CONF_PORT]
    host = config[CONF_HOST]
    machine_id = config[CONF_DEVICE_ID]
    system_class = config[CONF_DEVICE_CLASS]
    
    aidoo_args = {"speed_as_per": config[CONF_SPEED_PERCENTAGE]}    
    
    machine = airzone_factory(host, port, machine_id, system_class, **aidoo_args)

    if system_class == 'aidoo':
        from aidoo import Aidoo as Machine
        devices = [Machine(machine)]
    else:
        if system_class == 'localapi':
            from localapi import LocalAPIMachine as Machine
            from localapi import  LocalAPIZone as Zone
        if system_class == 'innobus':
            from innobus import InnobusMachine as Machine
            from innobus import  InnobusZone as Zone
        devices = [Machine(machine)] + [Zone(z) for z in machine.get_zones()]
        
    _LOGGER.info("Airzone devices " + str(devices) + " " + str(len(devices)))
    return devices

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    devices = await hass.async_add_executor_job(get_devices(config))
    async_add_entities(devices, update_before_add=True)

def setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    devices = get_devices(config)    
    add_entities(devices)
