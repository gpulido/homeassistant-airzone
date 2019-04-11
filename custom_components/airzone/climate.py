"""
Support for Airzone thermostats
"""
import logging
from homeassistant.components.climate import ClimateDevice

from homeassistant.components.climate.const import (
    STATE_AUTO, STATE_MANUAL, SUPPORT_OPERATION_MODE, 
    ATTR_TARGET_TEMP_HIGH, ATTR_TARGET_TEMP_LOW,
    SUPPORT_TARGET_TEMPERATURE, SUPPORT_FAN_MODE, SUPPORT_HOLD_MODE, 
    SUPPORT_AUX_HEAT, SUPPORT_ON_OFF)

from homeassistant.const import (CONF_HOST, CONF_PORT, ATTR_TEMPERATURE, TEMP_CELSIUS)
from datetime import timedelta
from enum import Enum

REQUIREMENTS = ['python-airzone==0.1.0']

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE | \
                SUPPORT_HOLD_MODE | SUPPORT_ON_OFF | SUPPORT_FAN_MODE

SUPPORT_FLAGS_MACHINE = SUPPORT_OPERATION_MODE 

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
    # ATTR_IS_ZONE_GRID_OPENED: 'is_zone_grid_opened',
    # ATTR_IS_GRID_MOTOR_ACTIVE: 'is_grid_motor_active',
    # ATTR_IS_GRID_MOTOR_REQUESTED: 'is_grid_motor_requested',
    ATTR_IS_FLOOR_ACTIVE: 'is_floor_active',
    # ATTR_LOCAL_MODULE_FANCOIL: 'get_local_module_fancoil',
    # ATTR_IS_REQUESTING_AIR: 'is_requesting_air',
    # ATTR_IS_OCCUPIED: 'is_occupied',
    # ATTR_IS_WINDOWS_OPENED: 'is_window_opened',
    # ATTR_FANCOIL_SPEED: 'get_fancoil_speed',
    # ATTR_PROPORTIONAL_APERTURE: 'get_proportional_aperture',
    # ATTR_TACTO_CONNECTED: 'is_tacto_connected_cz',
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
        return SUPPORT_FLAGS

    @property
    def temperature_unit(self):
        """Return the unit of measurement that is used."""
        return TEMP_CELSIUS

    @property
    def is_on(self):
        """Return true if the device is on."""
        return bool(self._airzone_zone.is_tacto_on())
    
    def turn_on(self):
        """Turn on."""
        self._airzone_zone.turnon_tacto()

    def turn_off(self):
        """Turn off."""
        self._airzone_zone.turnoff_tacto()

    @property
    def current_hold_mode(self):
        """Return hold mode setting."""
        return bool(self._airzone_zone.is_zone_hold())
    
    def set_hold_mode(self, hold_mode):
        """Update hold_mode on."""
        if hold_mode:
            self._airzone_zone.turnon_hold() 
        else:
            self._airzone_zone.turnoff_hold() 

    @property
    def current_operation(self):
        """Return current operation ie. heat, cool, idle."""
        from airzone.protocol import ZoneMode
        current_op = self._airzone_zone.get_zone_mode()
        return current_op.name

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return self._operational_modes

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

    def set_operation_mode(self, operation_mode):
        """Set new target operation mode."""
        self._airzone_zone.set_zone_mode(operation_mode)
        return
        
    @property
    def min_temp(self):
        return self._airzone_zone.get_min_signal_value()

    @property
    def max_temp(self):
        return self._airzone_zone.get_max_signal_value()
    
    @property
    def current_fan_mode(self):
        """Return the fan setting."""
        from airzone.protocol import FancoilSpeed
        return self._airzone_zone.get_speed_selection().name
    
    def set_fan_mode(self, fan_mode):
        self._airzone_zone.set_speed_selection(fan_mode)

    @property   
    def fan_list(self):
        return self._fan_list
    
    async def async_update(self):
        self._airzone_zone.retrieve_zone_status()
        self._state_attrs[ATTR_IS_FLOOR_ACTIVE] = self._airzone_zone.is_floor_active()
        # self._state_attrs.update(
        #         {key: self._extract_value_from_attribute(self._airzone_zone, value) for
        #          key, value in self._available_attributes.items()})
        _LOGGER.debug(str(self._airzone_zone))

    @staticmethod
    def _extract_value_from_attribute(state, attribute):
        value = getattr(state, attribute)
        if isinstance(value, Enum):
            return value.value

        return value

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
        return SUPPORT_FLAGS_MACHINE

    @property
    def temperature_unit(self):
        """Return the unit of measurement that is used."""
        return TEMP_CELSIUS

    @property
    def current_operation(self):
        from airzone.protocol import MachineOperationMode
        """Return current operation ie. heat, cool, idle."""
        current_op = self._airzone_machine.get_operation_mode()
        return current_op.name

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return self._operational_modes

    def set_operation_mode(self, operation_mode):
        """Set new target operation mode."""
        self._airzone_machine.set_operation_mode(operation_mode)
    
    def update(self):
        self._airzone_machine.retrieve_machine_status(False)
        _LOGGER.debug(str(self._airzone_machine))