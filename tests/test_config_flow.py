"""Tests for the config flow."""
from unittest import mock

from homeassistant.const import CONF_DEVICE_CLASS, CONF_DEVICE_ID, CONF_HOST, CONF_PORT
from pytest_homeassistant_custom_component.common import MockConfigEntry, patch

from custom_components.airzone import config_flow
from custom_components.airzone.const import DOMAIN


async def test_flow_user_init(hass):
    """Test the initialization of the form in the first step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    expected = {
        "data_schema": config_flow.AIRZONE_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": "airzone",
        "step_id": "user",
        "type": "form",
    }
    assert expected == result


@patch("custom_components.airzone.climate.airzone_factory")
async def test_add_airzone(m_airzone_factory, hass):
    """Test config flow options."""
    m_instance = mock.MagicMock()
    m_airzone_factory.return_value = m_instance
    m_instance._machineId = 1
    m_instance.get_local_temperature.return_value = 23
    m_instance.get_signal_temperature_value.return_value = 25
    m_instance.get_speed.return_value = 0
    m_instance.unique_id.return_value = "aido_1"

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="airzone_aido",
        data={
            CONF_HOST: "192.168.1.10",
            CONF_PORT: "5020",
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_CLASS: "aido",
        },
    )
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
