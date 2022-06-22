import logging
from datetime import timedelta
from typing import Callable, Optional

from homeassistant import config_entries, core
from homeassistant.components.climate import PLATFORM_SCHEMA
from homeassistant.const import CONF_DEVICE_CLASS, CONF_DEVICE_ID, CONF_HOST, CONF_PORT, CONF_PASSWORD, CONF_ENTITY_ID, \
    CONF_EMAIL, CONF_ID
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
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


def airzone_factory(address, port, machineId, system="innobus", **kwargs):
    if system == 'localapi':
        from airzone.localapi import Machine, API
        api = API(address, port)
        m = Machine(api, machineId)
    elif system == 'airzone_cloud':
        m = generate_airzone_cloud(address, port, **kwargs)
    else:
        from airzone.protocol import Gateway
        gat = Gateway(address, port)
        if system == 'innobus':
            from airzone.innobus import Machine
            m = Machine(gat, machineId)
        else:
            from airzone.aido import Aido
            m = Aido(gat, machineId, **kwargs)
    return m


def generate_airzone_cloud(email, password, **kwargs):
    from .airzone_cloud import AirzoneCloud
    return AirzoneCloud(email, password, **kwargs)


async def async_get_devices(config, hass):
    system_class = config[CONF_DEVICE_CLASS]
    if system_class == 'airzone_cloud':
        return await async_get_devices_cloud(config, hass)
    else:
        return await async_get_devices_local(config, hass)


async def async_get_devices_cloud(config, hass):
    email = config[CONF_EMAIL]
    password = config[CONF_PASSWORD]
    args = {"installation": config[CONF_ENTITY_ID], "group": config[CONF_ID], "device": config[CONF_DEVICE_ID]}

    machine = await hass.async_add_executor_job(lambda: generate_airzone_cloud(email, password, **args))

    from .airzone_cloud_entity import AirzoneCloudEntity as Machine
    devices = [Machine(machine)]

    _LOGGER.info("Airzone devices " + str(devices) + " " + str(len(devices)))
    return devices


async def async_get_devices_local(config, hass):
    port = config[CONF_PORT]
    host = config[CONF_HOST]
    machine_id = config[CONF_DEVICE_ID]
    system_class = config[CONF_DEVICE_CLASS]

    aidoo_args = {"speed_as_per": config[CONF_SPEED_PERCENTAGE]}

    machine = await hass.async_add_executor_job(lambda: airzone_factory(host, port, machine_id, system_class, **aidoo_args))

    if system_class == 'aidoo':
        from .aidoo import Aidoo as Machine
        devices = [Machine(machine)]
    else:
        # TODO: Review to unify the innobus and localapi management
        if system_class == 'localapi':
            if len(machine.zones) == 1:
                from .localapi import LocalAPIOneZone as Machine
                devices = [Machine(machine)]
            else:
                from .localapi import LocalAPIMachine as Machine
                from .localapi import LocalAPIZone as Zone
                devices = [Machine(machine)] + [Zone(z) for z in machine.zones]
        elif system_class == 'innobus':
            from .innobus import InnobusMachine as Machine
            from .innobus import  InnobusZone as Zone
            devices = [Machine(machine)] + [Zone(z) for z in machine.zones]

    _LOGGER.info("Airzone devices " + str(devices) + " " + str(len(devices)))
    return devices


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    devices = await async_get_devices(config, hass)
    async_add_entities(devices, update_before_add=True)


async def async_setup_platform(
    hass: core.HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    devices = await async_get_devices(config, hass)
    async_add_entities(devices)
