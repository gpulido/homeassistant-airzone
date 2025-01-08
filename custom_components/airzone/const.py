DOMAIN = "airzone"
DEFAULT_DEVICE_ID = 1
DEFAULT_DEVICE_CLASS = 'innobus'
DEFAULT_SPEED_AS_PER = False
SYSTEM_TYPES = ["innobus", "aidoo", "localapi"]
from airzone.localapi import OperationMode
from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    PRESET_NONE,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import Platform

PLATFORMS = [Platform.CLIMATE]


### Innobus Extra Attributes
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
ATTR_IS_AUTOMATIC_MODE = 'is_automatic_mode'
ATTR_IS_TACTO_ON = 'is_tacto_on'
ATTR_DIF_CURRENT_TEMP = 'get_dif_current_temp'

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
    ATTR_IS_AUTOMATIC_MODE: 'is_automatic_mode',
    ATTR_IS_TACTO_ON: 'is_tacto_on',
    ATTR_DIF_CURRENT_TEMP: 'get_dif_current_temp'
}

ZONE_HVAC_MODES = [HVACMode.AUTO, HVACMode.HEAT_COOL,  HVACMode.OFF]
PRESET_SLEEP = 'SLEEP'
ZONE_PRESET_MODES = [PRESET_NONE, PRESET_SLEEP]
ZONE_FAN_MODES = {FAN_AUTO: 'AUTOMATIC', FAN_LOW: 'SPEED_1', FAN_MEDIUM: 'SPEED_2', FAN_HIGH: 'SPEED_3'}
ZONE_FAN_MODES_R = dict(zip(ZONE_FAN_MODES.values(),ZONE_FAN_MODES.keys()))
ZONE_SUPPORT_FLAGS = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.PRESET_MODE

MACHINE_HVAC_MODES = [HVACMode.FAN_ONLY, HVACMode.HEAT,  HVACMode.COOL,  HVACMode.OFF]
PRESET_COMBINED_MODE = 'AIR&FLOOR'
PRESET_AIR_MODE = 'AIRE'
PRESET_FLOOR_MODE = 'FLOOR'
MACHINE_PRESET_MODES = [PRESET_AIR_MODE, PRESET_FLOOR_MODE, PRESET_COMBINED_MODE]
MACHINE_SUPPORT_FLAGS = ClimateEntityFeature.PRESET_MODE

# LocalAPI Modes

LOCALAPI_ZONE_HVAC_MODES = [HVACMode.HEAT_COOL,  HVACMode.OFF]
LOCALAPI_ZONE_SUPPORT_FLAGS =  ClimateEntityFeature.TARGET_TEMPERATURE

LOCALAPI_MACHINE_SUPPORT_FLAGS =  ClimateEntityFeature.FAN_MODE

LOCALAPI_MACHINE_HVAC_MODES = [ HVACMode.OFF, 
                             HVACMode.COOL, 
                            HVACMode.HEAT, 
                            HVACMode.FAN_ONLY, 
                            HVACMode.DRY,
                            HVACMode.AUTO] 


LOCALAPI_HVAC_MODE_MAP = {
    HVACMode.OFF: OperationMode.STOP,
    HVACMode.COOL: OperationMode.COOLING,
    HVACMode.HEAT: OperationMode.HEATING,
    HVACMode.FAN_ONLY: OperationMode.FAN,
    HVACMode.DRY: OperationMode.DRY,
    HVACMode.AUTO: OperationMode.AUTO
}

LOCALAPI_MODE_TO_HVAC_MAP = {
    'STOP':  HVACMode.OFF,
    'COOLING':  HVACMode.COOL,
    'AUTO': HVACMode.AUTO,
    'HEATING': HVACMode.HEAT,
    'FAN': HVACMode.FAN_ONLY,
    'DRY': HVACMode.DRY
}



#AIDO extra modes

CONF_SPEED_PERCENTAGE = "speed_as_percentage"

AIDO_HVAC_MODES = [HVACMode.AUTO, 
                   HVACMode.FAN_ONLY, 
                   HVACMode.HEAT, 
                   HVACMode.COOL, 
                   HVACMode.OFF, 
                   HVACMode.DRY]

#TODO: SWING_MODES =Louvres?
AIDO_SUPPORT_FLAGS = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE

AIDO_HVAC_MODE_MAP = {
    HVACMode.COOL:'COOLING',
    HVACMode.AUTO:'AUTO',
    HVACMode.HEAT:'HEATING',
    HVACMode.FAN_ONLY:'FAN',
    HVACMode.DRY:'DRY'
}

AIDO_MODE_TO_HVAC_MAP = {
    'COOLING':  HVACMode.COOL,
    'AUTO': HVACMode.AUTO,
    'HEATING': HVACMode.HEAT,
    'FAN': HVACMode.FAN_ONLY,
    'DRY': HVACMode.DRY
}
