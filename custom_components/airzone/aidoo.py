import logging
from typing import List, Optional

from homeassistant.components.climate import FAN_AUTO, ClimateEntity, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from .const import (
    AIDO_HVAC_MODE_MAP,
    AIDO_HVAC_MODES,
    AIDO_MODE_TO_HVAC_MAP,
    AIDO_SUPPORT_FLAGS,
)

_LOGGER = logging.getLogger(__name__)

class Aidoo(ClimateEntity):
    """Representation of a Aidoo Machine."""

    def __init__(self, airzone_aidoo):
        super().__init__()
        """Initialize the device."""
        self._name = "Aidoo "  + str(airzone_aidoo._machineId)
        _LOGGER.info("Airzone configure machine " + self._name)
        self._airzone_aidoo = airzone_aidoo
        
        #TODO: the fan available modes must be configured by the setup
        self._fan_modes = [FAN_AUTO] + [str(n) for n in range(1, airzone_aidoo.get_speed_steps() + 1)]        
        self._min_temp = 17
        self._max_temp = 35

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def supported_features(self):
        """Return the list of supported features."""        
        return AIDO_SUPPORT_FLAGS


    @property
    def temperature_unit(self):
        """Return the unit of measurement that is used."""
        return UnitOfTemperature.CELSIUS 

    def turn_on(self):
        """Turn on."""
        self._airzone_aidoo.turn_on()

    def turn_off(self):
        """Turn off."""
        self._airzone_aidoo.turn_off()

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVACMode.*.
        """        
        if not self._airzone_aidoo.get_is_machine_on():
            return HVACMode.OFF

        current_op = self._airzone_aidoo.get_operation_mode().name
        return AIDO_MODE_TO_HVAC_MAP[current_op]        


    @property
    def hvac_modes(self) -> List[HVACMode]:
        """Return the list of available hvac operation modes.
        Need to be a subset of HVAC_MODES.
        """        
        return AIDO_HVAC_MODES

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
            return

        self._airzone_aidoo.set_operation_mode(AIDO_HVAC_MODE_MAP[hvac_mode])       
    
    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._airzone_aidoo.get_local_temperature()

    @property
    def target_temperature(self):
        return self._airzone_aidoo.get_signal_temperature_value()

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return None
        self._airzone_aidoo.set_signal_temperature_value(round(float(temperature), 1))

    @property
    def fan_mode(self) -> Optional[str]:
        """Return the fan setting.        
        """        
        fan_mode = self._airzone_aidoo.get_speed().value
        if fan_mode == 0:
            return FAN_AUTO
        return str(fan_mode)
    
    def set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        if fan_mode == FAN_AUTO:
            self._airzone_aidoo.set_speed('AUTO')
            return
        self._airzone_aidoo.set_speed(f'SPEED_{fan_mode}')

    @property
    def fan_modes(self) -> Optional[List[str]]:
        """Return the list of available fan modes.        
        """
        return self._fan_modes
    
    @property
    def min_temp(self):        
        return self._min_temp

    @property
    def max_temp(self):        
        return self._max_temp

    @property
    def unique_id(self):
        return self._airzone_aidoo.unique_id()


    async def async_update(self):
        self._airzone_aidoo._retrieve_machine_state()
        _LOGGER.debug(str(self._airzone_aidoo))
