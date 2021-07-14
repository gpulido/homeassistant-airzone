import logging
from typing import List

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVAC_MODE_HEAT_COOL, HVAC_MODE_OFF
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT

from .const import (
    LOCALAPI_HVAC_MODE_MAP,
    LOCALAPI_MODE_TO_HVAC_MAP,
    LOCALAPI_ZONE_HVAC_MODES,
    LOCALAPI_ZONE_SUPPORT_FLAGS,
)

_LOGGER = logging.getLogger(__name__)


class LocalAPIZone(ClimateEntity):
    """Representation of a LocalAPI Zone."""

    def __init__(self, airzone_zone):
        """Initialize the device."""        
        self.airzone_zone = airzone_zone                
        _LOGGER.info("Airzone configure zone " + self._name)
        

    @property
    def airzone_zone(self):
        return self._airzone_zone

    @property.setter
    def airzone_zone(self, value):
        self._airzone_zone = value
        self._name = value.name
        from airzone.localapi import TempUnits
        self._units = TEMP_CELSIUS
        if value.units == TempUnits.FAHRENHEIT:
            self._units = TEMP_FAHRENHEIT        

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return LOCALAPI_ZONE_SUPPORT_FLAGS

    @property
    def temperature_unit(self):
        """Return the unit of measurement that is used."""        
        return self._units

    def turn_on(self):
        """Turn on."""
        self._airzone_zone.turn_on()

    def turn_off(self):
        """Turn off."""
        self._airzone_zone.turn_off()

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*.
        """
        if self.airzone_zone.is_on():            
        	return HVAC_MODE_HEAT_COOL
        else:
            return HVAC_MODE_OFF

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes.
        Need to be a subset of HVAC_MODES.
        """
        return LOCALAPI_ZONE_HVAC_MODES

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_OFF:
            self._airzone_zone.turn_off()

        elif hvac_mode == HVAC_MODE_HEAT_COOL:
            self._airzone_zone.turn_on()

    #TODO: review if we can extract running hvac
    # @property
    # def hvac_action(self) -> Optional[str]:
    #     """Return the current running hvac operation."""    
    #     op_mode = self._airzone_zone._machine.get_operation_mode().name

    #     if self._airzone_zone.is_floor_active():
    #         return CURRENT_HVAC_HEAT

    #     if self._airzone_zone.is_requesting_air():
    #         if op_mode == 'HOT_AIR':
    #             return CURRENT_HVAC_HEAT
    #         return CURRENT_HVAC_COOL

    #     if op_mode == 'STOP':
    #         return CURRENT_HVAC_OFF
    #     return CURRENT_HVAC_IDLE


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
        self._airzone_zone.signal_temperature_value = round(float(temperature), 1)

        
    @property
    def min_temp(self):
        return self._airzone_zone.min_temp

    @property
    def max_temp(self):
        return self._airzone_zone.max_temp
    
    @property
    def unique_id(self):
        return self._airzone_zone.unique_id

    def update(self):
        # Really not needed as the machine is the one that updates all      
        _LOGGER.debug(str(self._airzone_zone))



class LocalAPIMachine(ClimateEntity):
    """Representation of a LocalAPI Machine."""

    def __init__(self, airzone_machine):
        """Initialize the device."""
        self._name = "Airzone Machine "  + str(airzone_machine._machineId)
        _LOGGER.info("Airzone configure machine " + self._name)
        self.airzone_machine = airzone_machine
        
    @property
    def airzone_machine(self):
        return self._airzone_machine
    
    @airzone_machine.setter
    def airzone_machine(self, value):
        self._airzone_machine = value        
        from airzone.localapi import TempUnits
        self._units = TEMP_CELSIUS
        if value.units == TempUnits.FAHRENHEIT:
            self._units = TEMP_FAHRENHEIT    

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement that is used."""
        return self._units

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*.
        """        
        current_op = self.airzone_machine.operation_mode.name
        return LOCALAPI_MODE_TO_HVAC_MAP[current_op]        

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes.
        Need to be a subset of HVAC_MODES.
        """
        return LOCALAPI_ZONE_HVAC_MODES

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        new_op = LOCALAPI_HVAC_MODE_MAP[hvac_mode]     
        self._airzone_machine.set_operation_mode(new_op)            

    @property
    def unique_id(self):
        return self._airzone_machine.unique_id


    async def async_update(self):
        self.airzone_machine.retrieve_system_data()
        _LOGGER.debug(str(self.airzone_machine))
