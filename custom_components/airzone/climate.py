"""
Support for Airzone thermostats
"""
import logging
from homeassistant.components.climate import ClimateDevice

from homeassistant.components.climate.const import {
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    SUPPORT_AUX_HEAT
    HVAC_MODE_AUTO,
    HVAC_MODE_OFF,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_FAN_MODEOFF,
    HVAC_MODES,
    PRESET_NONE,
}

from homeassistant.const import (CONF_HOST, CONF_PORT, ATTR_TEMPERATURE, TEMP_CELSIUS)
from datetime import timedelta
from enum import Enum

REQUIREMENTS = ['python-airzone==0.1.0']

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)



ATTR_IS_ZONE_GRID_OPENED = 'is_zone_grid_opened'
ATTR_IS_GRID_MOTOR_ACTIVE = 'is_grid_motor_active'
ATTR_IS_GRID_MOTOR_REQUESTED = 'is_grid_motor_requested'
ATTR_IS_FLOOR_ACTIVE = 'is_floor_active'
ATTR_LOCAL_MODULE_FANCOIL = 'get_local_module_fancoil'
ATTR_IS_REQUESTING_AIR = 'is_requesting_air'
ATTR_IS_OCCUPIED = 'is_occupied'
ATTR_IS_WINDOWS_OPENED = 'is_window_opened'
ATTR_FANCOIL_SPEED = 'get_fancoil_speed'
ATTR_PROPORTIONAL_APERTURE = 'get_proportional_aperture'
ATTR_TACTO_CONNECTED = 'is_tacto_connected_cz'

AVAILABLE_ATTRIBUTES_ZONE = {
    ATTR_IS_ZONE_GRID_OPENED: 'is_zone_grid_opened',
    ATTR_IS_GRID_MOTOR_ACTIVE: 'is_grid_motor_active',
    ATTR_IS_GRID_MOTOR_REQUESTED: 'is_grid_motor_requested',
    ATTR_IS_FLOOR_ACTIVE: 'is_floor_active',
    ATTR_LOCAL_MODULE_FANCOIL: 'get_local_module_fancoil',
    ATTR_IS_REQUESTING_AIR: 'is_requesting_air',
    ATTR_IS_OCCUPIED: 'is_occupied',
    ATTR_IS_WINDOWS_OPENED: 'is_window_opened',
    ATTR_FANCOIL_SPEED: 'get_fancoil_speed',
    ATTR_PROPORTIONAL_APERTURE: 'get_proportional_aperture',
    ATTR_TACTO_CONNECTED: 'is_tacto_connected_cz',
}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Airzone thermostat platform."""
    port = config.get(CONF_PORT)
    host = config.get(CONF_HOST)
    if port is None or host is None:
        return
    from airzone import Gateway
    gat = Gateway(host, port, 1)
    devices = [InnobusMachine(gat._Machine)]+[InnobusZone(z) for z in gat.devices]
    _LOGGER.info("Airzone devices " + str(devices) + " " + str(len(devices)))
    add_entities(devices)

ZONE_HVAC_MODES = [HVAC_MODE_AUTO, HVAC_HEAT_COOL, HVAC_MODE_OFF]
PRESET_SLEEP = 'SLEEP'
ZONE_PRESET_MODES = [PRESET_NONE, PRESET_SLEEP]
ZONE_FAN_MODES = [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
ZONE_SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE | SUPPORT_PRESET_MODE


class InnobusZone(ClimateDevice):
    """Representation of a Innobus Zone."""

    def __init__(self, airzone_zone):
        """Initialize the device."""
        self._name = "Airzone Zone "  + str(airzone_zone.zoneId)
        _LOGGER.info("Airzone configure zone " + self._name)
        self._airzone_zone = airzone_zone
        from airzone.protocol import ZoneMode
        self._operational_modes = [e.name for e in ZoneMode]
        from airzone.protocol import FancoilSpeed
        self._fan_list = [e.name for e in FancoilSpeed]

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
        return TEMP_CELSIUS

    
    def turn_on(self):
        """Turn on."""
        self._airzone_zone.turnon_tacto()

    def turn_off(self):
        """Turn off."""
        self._airzone_zone.turnoff_tacto()


    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*.
        """
        tacto_on =  bool(self._airzone_zone.is_tacto_on())
        if tacto_on:
            return HVAC_MODE_AUTO
        else:
            return HVAC_MODE_OFF

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes.
        Need to be a subset of HVAC_MODES.
        """
        return ZONE_HVAC_MODES

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_OFF:
            self._airzone_zone.turnoff_automatic_mode()
            self._airzone_zone.turnoff_tacto()
        elif hvac_mode == HVAC_MODE_HEAT_COOL:
            self._airzone_zone.turnon_tacto()
        elif hvac_mode == HVAC_MODE_AUTO:
            self._airzone_zone.turnon_automatic_mode()

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._airzone_zone.get_local_temperature()

    @property
    def target_temperature(self):
        return self._airzone_zone.get_signal_temperature_value()

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return None
        print("Airzone temperature: " + str(temperature))
        self._airzone_zone.set_signal_temperature_value(round(float(temperature), 1))

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp.
        Requires SUPPORT_PRESET_MODE.
        """
        if self._airzone_machine.is_sleep_on():
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
        Requires SUPPORT_FAN_MODE.
        """
        from airzone.protocol import FancoilSpeed
        fan_mode = self._airzone_zone.get_speed_selection()
        if fan_mode == FancoilSpeed.AUTOMATIC:
            return FAN_AUTO
        if fan_mode == FancoilSpeed.SPEED_1:
            return FAN_LOW
        if fan_mode == FancoilSpeed.SPEED_2:
            return FAN_MEDIUM
        if fan_mode == FancoilSpeed.SPEED_3:
            return FAN_HIGH
        return FAN_AUTO


    @property
    def fan_modes(self) -> Optional[List[str]]:
        """Return the list of available fan modes.
        Requires SUPPORT_FAN_MODE.
        """
        return ZONE_FAN_MODES
    
    def set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        
        if fan_mode == FAN_AUTO:
            self._airzone_zone.get_speed_selection('AUTOMATIC')
            return
        if fan_mode == FAN_LOW:
            self._airzone_zone.get_speed_selection('SPEED_1')
            return FAN_LOW
        if fan_mode == FAN_MEDIUM:
            self._airzone_zone.get_speed_selection('SPPED_2')
            return FAN_MEDIUM
        if fan_mode == FAN_HIGH:
            self._airzone_zone.get_speed_selection('SPEED_3')
                   
    @property
    def min_temp(self):
        return self._airzone_zone.get_min_signal_value()

    @property
    def max_temp(self):
        return self._airzone_zone.get_max_signal_value()
    
    async def async_update(self):
        self._airzone_zone.retrieve_zone_status()
        #self._state_attrs[ATTR_IS_FLOOR_ACTIVE] = self._airzone_zone.is_floor_active()
        self._state_attrs.update(
                {key: self._extract_value_from_attribute(self._airzone_zone, value) for
                 key, value in self._available_attributes.items()})
        _LOGGER.debug(str(self._airzone_zone))

    @staticmethod
    def _extract_value_from_attribute(state, attribute):
        func = getattr(state, attribute)
        value = func()
        if isinstance(value, Enum):
            return value.value
        return value

MACHINE_HVAC_MODES = [HVAC_MODE_FAN_ONLY, HVAC_HEAT, HVAC_MODE_COOL, HVAC_MODE_OFF]
PRESET_AIR_MODE = 'AIRE'
PRESET_RADIATOR_MODE = 'RADIADOR'
MACHINE_PRESET_MODES = [PRESET_AIR_MODE, PRESET_RADIATOR_MODE], 
MACHINE_SUPPORT_FLAGS = SUPPORT_AUX_HEAT | SUPPORT_PRESET_MODE
class InnobusMachine(ClimateDevice):
    """Representation of a Innobus Zone."""

    def __init__(self, airzone_machine):
        """Initialize the device."""
        self._name = "Airzone Machine "  + str(airzone_machine._machineId)
        _LOGGER.info("Airzone configure machine " + self._name)
        self._airzone_machine = airzone_machine
        from airzone.protocol import MachineOperationMode
        self._operational_modes = [e.name for e in MachineOperationMode]

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
        return TEMP_CELSIUS

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*.
        """
        from airzone.protocol import MachineOperationMode
        current_op = self._airzone_machine.get_operation_mode()
        if current_op in [MachineOperationMode.HOT, MachineOperationMode.HOT_AIR, MachineOperationMode.HOTPLUS]:
            return HVAC_MODE_HEAT
        if current_op == MachineOperationMode.COLD:
            return HVAC_MODE_COOL
        if current_op == MachineOperationMode.AIR:
            return HVAC_MODE_FAN_ONLY
        return HVAC_MODE_OFF
            

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes.
        Need to be a subset of HVAC_MODES.
        """
        return MACHINE_HVAC_MODES
    
     def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_OFF:
            self._airzone_machine.set_operation_mode('STOP')
            return
        if hvac_mode == HVAC_MODE_COOL:
            self._airzone_machine.set_operation_mode('COLD')
            return
        if hvac_mode == HVAC_MODE_FAN_ONLY:
            self._airzone_machine.set_operation_mode('AIR')
            return
         if hvac_mode == HVAC_MODE_HEAT:
            if self.is_aux_heat:
                self._airzone_machine.set_operation_mode('HOTPLUS')
                return
            if self.preset_mode == PRESET_AIR_MODE:
                self._airzone_machine.set_operation_mode('HOT_AIR')
                return
            if self.preset_mode == PRESET_RADIATOR_MODE:
                self._airzone_machine.set_operation_mode('HOT')
                return
            

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp.
        Requires SUPPORT_PRESET_MODE.
        """
        from airzone.protocol import MachineOperationMode
        current_op = self._airzone_machine.get_operation_mode()
        if current_op in [MachineOperationMode.HOT_AIR]
            return PRESET_AIR_MODE
        else
            return PRESET_RADIATOR_MODE

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes.
        Requires SUPPORT_PRESET_MODE.
        """
        return MACHINE_PRESET_MODES

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if self.hvac_mode == HVAC_MODE_HEAT:

            if preset_mode == PRESET_RADIATOR_MODE:
                self._airzone_machine.set_operation_mode('HOT')
                return
            if preset_mode == PRESET_AIR_MODE:
                self._airzone_machine.set_operation_mode('HOT_AIR')
                return

    def turn_aux_heat_on(self) -> None:
        """Turn auxiliary heater on."""
        self._airzone_machine.set_operation_mode('HOTPLUS')
    
    def turn_aux_heat_off(self) -> None:
        """Turn auxiliary heater on."""
        if self.preset_mode == PRESET_AIR_MODE:
            self._airzone_machine.set_operation_mode('AIR')
        elif self.preset_mode == PRESET_RADIATOR_MODE:
            self._airzone_machine.set_operation_mode('HOT')
    
    @property
    def is_aux_heat(self) -> Optional[bool]:
        """Return true if aux heater.
        Requires SUPPORT_AUX_HEAT.
        """
        from airzone.protocol import MachineOperationMode
        return self._airzone_machine.get_operation_mode() == MachineOperationMode.HOTPLUS
    
    def update(self):
        self._airzone_machine.retrieve_machine_status(False)
        _LOGGER.debug(str(self._airzone_machine))