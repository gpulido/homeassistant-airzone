"""Airzone Custom Component."""
from homeassistant import config_entries, core

from .const import DOMAIN, PLATFORMS


async def async_setup_entry(
    hass: core.HomeAssistant,
    entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the climate platform.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the GitHub Custom component from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True
