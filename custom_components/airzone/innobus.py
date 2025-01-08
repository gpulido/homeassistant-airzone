from enum import Enum
import logging
from typing import List, Optional

from homeassistant.components.climate import (
    PRESET_NONE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from .const import (
    AVAILABLE_ATTRIBUTES_ZONE,
    MACHINE_HVAC_MODES,
    MACHINE_PRESET_MODES,
    MACHINE_SUPPORT_FLAGS,
    PRESET_AIR_MODE,
    PRESET_COMBINED_MODE,
    PRESET_FLOOR_MODE,
    PRESET_SLEEP,
    ZONE_FAN_MODES,
    ZONE_FAN_MODES_R,
    ZONE_HVAC_MODES,
    ZONE_PRESET_MODES,
    ZONE_SUPPORT_FLAGS,
)

_LOGGER = logging.getLogger(__name__)



class InnobusZone(ClimateEntity):
    """Representation of a Innobus Zone."""

    def __init__(self, airzone_zone):
        """Initialize the device."""
        self._name = "Airzone Zone "  + str(airzone_zone._zone_id)
        _LOGGER.info("Airzone configure zone " + self._name)
        self._airzone_zone = airzone_zone
        self._available_attributes = AVAILABLE_ATTRIBUTES_ZONE
        self._state_attrs = {}
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes})

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._state_attrs

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return ZONE_SUPPORT_FLAGS

    @property
    def temperature_unit(self):
        """Return the unit of measurement that is used."""
        return UnitOfTemperature.CELSIUS 


    def turn_on(self):
        """Turn on."""
        self._airzone_zone.turn_on()

    def turn_off(self):
        """Turn off."""
        self._airzone_zone.turn_off()

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*.
        """
        tacto_on =  bool(self._airzone_zone.is_tacto_on())
        auto_on = bool(self._airzone_zone.is_automatic_mode())
        if tacto_on and auto_on:
            return HVACMode.AUTO
        elif tacto_on and not auto_on:
            return HVACMode.HEAT_COOL
        else:
            return HVACMode.OFF

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available hvac operation modes.
        Need to be a subset of HVAC_MODES.
        """
        return ZONE_HVAC_MODES

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            self._airzone_zone.turnoff_tacto()

        elif hvac_mode == HVACMode.HEAT_COOL:
            self._airzone_zone.turnoff_automatic_mode()
            self._airzone_zone.retrieve_zone_state()
            self._airzone_zone.turnon_tacto()

        elif hvac_mode == HVACMode.AUTO:
            self._airzone_zone.turnon_automatic_mode()
            self._airzone_zone.retrieve_zone_state()
            self._airzone_zone.turnon_tacto()

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation."""
        op_mode = self._airzone_zone._machine.operation_mode.name

        if self._airzone_zone.is_floor_active():
            return HVACAction.HEATING

        if self._airzone_zone.is_requesting_air():
            if op_mode == 'HOT_AIR':
                return HVACAction.HEATING
            return HVACAction.COOLING

        if op_mode == 'STOP':
            return HVACAction.OFF
        return HVACAction.IDLE


    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._airzone_zone.local_temperature

    @property
    def target_temperature(self):
        return self._airzone_zone.signal_temperature_value

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return None
        self._airzone_zone.set_signal_temperature_value(round(float(temperature), 1))

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp.
        Requires SUPPORT_PRESET_MODE.
        """
        if self._airzone_zone.is_sleep_on():
            return PRESET_SLEEP
        return PRESET_NONE

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes.
        Requires SUPPORT_PRESET_MODE.
        """
        return ZONE_PRESET_MODES

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if preset_mode == PRESET_NONE:
            self._airzone_zone.turnoff_sleep()
        else:
            self._airzone_zone.turnon_sleep()

    @property
    def fan_mode(self) -> Optional[str]:
        """Return the fan setting.
        """
        fan_mode = self._airzone_zone.get_speed_selection().name
        return ZONE_FAN_MODES_R[fan_mode]


    @property
    def fan_modes(self) -> Optional[List[str]]:
        """Return the list of available fan modes.
        """
        return list(ZONE_FAN_MODES.keys())

    def set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        self._airzone_zone.set_speed_selection(ZONE_FAN_MODES[fan_mode])

    @property
    def unique_id(self):
        return self._airzone_zone.unique_id


    def update(self):
        self._airzone_zone.retrieve_zone_state()
        self._state_attrs.update(
                {key: self._extract_value_from_attribute(self._airzone_zone, value) for
                 key, value in self._available_attributes.items()})
        self._attr_max_temp = self._airzone_zone.max_temp
        self._attr_min_temp = self._airzone_zone.min_temp
        _LOGGER.debug(str(self._airzone_zone))

    @staticmethod
    def _extract_value_from_attribute(state, attribute):
        func = getattr(state, attribute)
        value = func()
        if isinstance(value, Enum):
            return value.value
        return value


class InnobusMachine(ClimateEntity):
    """Representation of a Innobus Machine."""

    def __init__(self, airzone_machine):
        """Initialize the device."""
        self._name = "Airzone Machine "  + str(airzone_machine._machineId)
        _LOGGER.info("Airzone configure machine " + self._name)
        self._airzone_machine = airzone_machine

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return MACHINE_SUPPORT_FLAGS

    @property
    def temperature_unit(self):
        """Return the unit of measurement that is used."""
        return UnitOfTemperature.CELSIUS 

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*.
        """
        from airzone.innobus import OperationMode
        current_op = self._airzone_machine.operation_mode
        if current_op in [OperationMode.HOT, OperationMode.HOT_AIR, OperationMode.HOTPLUS]:
            return HVACMode.HEAT
        if current_op == OperationMode.COLD:
            return HVACMode.COOL
        if current_op == OperationMode.AIR:
            return HVACMode.FAN_ONLY
        return HVACMode.OFF


    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available hvac operation modes.
        Need to be a subset of HVAC_MODES.
        """
        return MACHINE_HVAC_MODES

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            self._airzone_machine.operation_mode = 'STOP'
            return
        if hvac_mode == HVACMode.COOL:
            self._airzone_machine.operation_mode = 'COLD'
            return
        if hvac_mode == HVACMode.FAN_ONLY:
            self._airzone_machine.operation_mode = 'AIR'
            return
        if hvac_mode == HVACMode.HEAT:
            if self.preset_mode == PRESET_COMBINED_MODE:
                self._airzone_machine.operation_mode = 'HOTPLUS'
                return
            if self.preset_mode == PRESET_AIR_MODE:
                self._airzone_machine.operation_mode = 'HOT_AIR'
                return
            if self.preset_mode == PRESET_FLOOR_MODE:
                self._airzone_machine.operation_mode = 'HOT'
                return


    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp.
        Requires SUPPORT_PRESET_MODE.
        """
        current_op = self._airzone_machine.operation_mode.name
        if current_op == 'HOT_AIR':
            return PRESET_AIR_MODE
        if current_op == 'HOTPLUS':
            return PRESET_COMBINED_MODE
        else:
            return PRESET_FLOOR_MODE

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes.
        Requires SUPPORT_PRESET_MODE.
        """
        return MACHINE_PRESET_MODES

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if self.hvac_mode == HVACMode.HEAT:
            if preset_mode == PRESET_FLOOR_MODE:
                self._airzone_machine.operation_mode = 'HOT'
                return
            if preset_mode == PRESET_AIR_MODE:
                self._airzone_machine.operation_mode = 'HOT_AIR'
                return
            if preset_mode == PRESET_COMBINED_MODE:
                self._airzone_machine.operation_mode = 'HOTPLUS'

    @property
    def unique_id(self):
        return self._airzone_machine.unique_id


    async def async_update(self):
        self._airzone_machine._retrieve_machine_state()
        _LOGGER.debug(str(self._airzone_machine))
