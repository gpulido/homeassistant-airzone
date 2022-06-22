from typing import Optional, List, Any
from datetime import datetime


class LocalTemp:
    fah: Optional[int]
    celsius: Optional[int]

    def __init__(self, dict1):
        self.__dict__.update(dict1)


class Manufacturer:
    id: int
    text: str

    def __init__(self, dict1):
        self.__dict__.update(dict1)


class Timer:
    value: int
    count: int

    def __init__(self, dict1):
        self.__dict__.update(dict1)


class MachineStatus:
    machineready: bool
    errors: List[Any]
    timer: Timer
    timer_values: List[int]
    manufacturer: Manufacturer
    power: bool
    aq_quality: None
    aqpm1_0: None
    aqpm2_5: None
    aqpm10: None
    active: bool
    step: LocalTemp
    tt_units: int
    mode: int
    mode_available: List[int]
    setpoint_air_cool: LocalTemp
    setpoint_air_heat: LocalTemp
    speed_values: List[int]
    speed_type: int
    speed_conf: int
    tai_temp: LocalTemp
    local_temp: LocalTemp
    setpoint_air_auto: LocalTemp
    range_sp_cool_air_max: LocalTemp
    range_sp_cool_air_min: LocalTemp
    range_sp_hot_air_max: LocalTemp
    range_sp_hot_air_min: LocalTemp
    range_sp_auto_air_max: LocalTemp
    range_sp_auto_air_min: LocalTemp
    pspeed: int
    block_autospeed: bool
    block_autotemp: bool
    block_dryspeed: bool
    block_drytemp: bool
    block_fantemp: bool
    name: str
    double_sp: bool
    dualsp_auto_conf: None
    autochange_diff_temp_conf: None
    is_connected: bool
    connection_date: datetime
    disconnection_date: datetime
    ws_connected: bool
    ws_sched_calendar_available: bool
    ws_sched_available: bool
    range_air_max: LocalTemp
    range_air_min: LocalTemp

    def __init__(self, dict1):
        self.__dict__.update(dict1)
