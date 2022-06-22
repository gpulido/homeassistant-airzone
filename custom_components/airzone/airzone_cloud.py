import json

import requests
import urllib3
from airzone.aido import Speed, OperationMode
from homeassistant.components.climate.const import HVAC_MODE_COOL, HVAC_MODE_HEAT, HVAC_MODE_AUTO, HVAC_MODE_OFF

from .machine_status import MachineStatus
from .const import AIDO_MODE_TO_HVAC_MAP

AIRZONECLOUD_API = "https://m.airzonecloud.com/api/v1"


class AirzoneCloud:

    def __init__(self, email: str, password: str, installation: int = 1, group: int = 1, device: int = 1):
        urllib3.disable_warnings()
        self._installation_number = (installation - 1)
        self._group_number = (group - 1)
        self._device_number = (device - 1)
        self._token, self._refresh_token = self.login(email, password)
        self._installation_id = self.get_installation_id()
        self._device_id = self.get_device_id()
        self._retrieve_machine_state()

    def get_is_machine_on(self):
        return self._machine_state.power

    def turn_on(self):
        self.execute_command({"params": {"power": True}})

    def turn_off(self):
        self.execute_command({"params": {"power": False}})

    def get_signal_temperature_value(self):
        if not self.get_is_machine_on():
            return None
        value = AIDO_MODE_TO_HVAC_MAP[self.get_operation_mode().name]
        temp = {
            HVAC_MODE_COOL: self._machine_state.setpoint_air_cool.celsius,
            HVAC_MODE_HEAT: self._machine_state.setpoint_air_heat.celsius,
            HVAC_MODE_AUTO: self._machine_state.setpoint_air_auto.celsius
        }.get(value, None)
        return None if temp is None else temp

    def set_signal_temperature_value(self, value):
        self.execute_command({"params": {"setpoint": value}, "opts": {"units": 0}})

    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*.
        """
        if not self._machine_state.get_is_machine_on():
            return HVAC_MODE_OFF

        current_op = self.get_operation_mode().name
        return AIDO_MODE_TO_HVAC_MAP[current_op]

    def get_local_temperature(self):
        return None if self._machine_state.local_temp.celsius is None else self._machine_state.local_temp.celsius

    def get_operation_mode(self):
        if self._machine_state is None:
            return OperationMode.AUTO
        return OperationMode(self._machine_state.mode)

    def set_operation_mode(self, operationMode):
        if not self.get_is_machine_on():
            self.turn_on()
        self.execute_command({"params": {"mode": OperationMode[operationMode].value}})

    def get_speed(self):
        if self._machine_state is None:
            return Speed.AUTO
        value = self._machine_state.pspeed * 4 // 100
        return Speed(value)

    def set_speed(self, speed):
        value = Speed[speed].value
        self.execute_command({"params": {"speed": (value * 100 // 4)}})

    def __str__(self):
        return "Aido with id: " + str(self.unique_id()) + \
               "On:" + str(self.get_is_machine_on()) + \
               "Operation Mode: " + str(self.get_operation_mode()) + \
               "Signal Temp: " + str(self.get_signal_temperature_value()) + \
               "Local Temp: " + str(self.get_local_temperature()) + \
               "Speed: " + str(self.get_speed())

    def unique_id(self):
        return f'Aido_M{self._installation_id}_{str(self._device_id)}'

    @property
    def machine_state(self):
        return self._machine_state

    def _retrieve_machine_state(self):
        self._machine_state = self.get_device_status()

    def login(self, email: str, password: str):
        payload = json.dumps({
            "email": "%s" % email,
            "password": "%s" % password
        })
        response = requests.post(
            "%s/auth/login" % AIRZONECLOUD_API,
            headers={"Content-Type": "application/json"},
            data=payload,
            verify=False
        )
        result = json.loads(response.content)
        return result["token"], result["refreshToken"]

    def refresh_token(self):
        response = requests.get(
            "{0}/auth/refreshToken/{1}".format(AIRZONECLOUD_API, self._refresh_token),
            headers={"Content-Type": "application/json"},
            verify=False
        )
        result = json.loads(response.content)
        self._token, self._refresh_token = result["token"], result["refreshToken"]

    def get_installation_id(self):
        response = self.call_get(
            "{0}/installations".format(AIRZONECLOUD_API),
            {"Authorization": "Bearer %s" % self._token}
        )
        return response["installations"][self._installation_number]["installation_id"]

    def get_device_id(self):
        response = self.call_get(
            "{0}/installations/{1}".format(AIRZONECLOUD_API, self._installation_id),
            {"Authorization": "Bearer %s" % self._token}
        )
        return response["groups"][self._group_number]["devices"][self._device_number]["device_id"]

    def get_device_status(self):
        response = self.call_get(
            "{0}/devices/{1}/status?installation_id={2}"
            .format(AIRZONECLOUD_API, self._device_id, self._installation_id),
            {"Authorization": "Bearer %s" % self._token}
        )
        return json.loads(json.dumps(response), object_hook=MachineStatus)

    def execute_command(self, command: dict):
        response = self.call_put(
            "{0}/installations/{1}".format(AIRZONECLOUD_API, self._installation_id),
            command,
            {"Authorization": "Bearer %s" % self._token, "Content-Type": "application/json"}
        )
        self._retrieve_machine_state()
        return response

    def call_get(self, url: str, headers: dict):
        return self.call("GET", url, headers=headers)

    def call_put(self, url: str, command: dict, headers: dict):
        return self.call("PUT", url, data=json.dumps(command), headers=headers)

    def call(self, method, url, **kwargs):
        response = requests.request(method, url, **kwargs, verify=False)
        if response.status_code == 401:
            self.refresh_token()
            kwargs["headers"]["Authorization"] = "Bearer " + self._token
            response = requests.request(method, url, **kwargs, verify=False)
        return json.loads(response.content) if response.content else None
