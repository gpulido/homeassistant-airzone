"""Tests for the climate module."""
from unittest.mock import MagicMock

from airzone.aido import OperationMode, Speed
from homeassistant.components.climate.const import FAN_AUTO, HVAC_MODE_COOL
from pytest_homeassistant_custom_component.common import (  # noqa: E811,F401
    MockConfigEntry,
    patch,
)

from custom_components.airzone.aidoo import Aidoo


async def test_aido_async_update_success(hass):
    """Tests a fully successful async_update."""

    airzone_aido = MagicMock()
    airzone_aido.get_local_temperature = MagicMock(return_value=24)
    airzone_aido.get_signal_temperature_value = MagicMock(return_value=22)
    airzone_aido.get_speed = MagicMock(return_value=Speed.SPEED_2)
    airzone_aido.get_is_machine_on = MagicMock(return_value=True)
    airzone_aido.get_operation_mode = MagicMock(return_value=OperationMode.COOLING)
    airzone_aido.get_speed_steps = MagicMock(return_value=4)
    aido = Aidoo(airzone_aido)
    aido.hass = hass
    await aido.async_update()

    expected = {"current_temperature": 24, "temperature": 22, "fan_mode": "2"}

    assert expected == aido.state_attributes
    assert aido.hvac_mode == HVAC_MODE_COOL
    assert aido.available is True


async def test_aido_async_test_fan_mode(hass):
    """Tests a fully successful async_update."""

    airzone_aido = MagicMock()
    airzone_aido.get_local_temperature = MagicMock(return_value=24)
    airzone_aido.get_signal_temperature_value = MagicMock(return_value=22)
    airzone_aido.get_speed = MagicMock(return_value=Speed.SPEED_2)
    airzone_aido.get_is_machine_on = MagicMock(return_value=True)
    airzone_aido.get_operation_mode = MagicMock(return_value=OperationMode.COOLING)
    airzone_aido.get_speed_steps = MagicMock(return_value=4)
    aido = Aidoo(airzone_aido)
    aido.hass = hass
    aido.set_fan_mode("1")
    assert aido.fan_modes == [FAN_AUTO, "1", "2", "3", "4"]
    airzone_aido.set_speed.assert_called_with("SPEED_1")
