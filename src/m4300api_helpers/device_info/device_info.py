"""Helper module for M4300 switch device information endpoint.

This module provides functionality to retrieve device information from an M4300
switch including hardware details, operational status, and sensor readings.

Note:
    SSL certificate verification is disabled as M4300 switches use
    self-signed certificates. This is a known and accepted limitation
    of the device's firmware.
"""

import json
from typing import TypedDict, Literal, List, Dict
import requests
from requests.exceptions import RequestException
from .. import ApiResult, ResponseData

# Default timeout for API requests (in seconds)
DEFAULT_TIMEOUT = 10

class TemperatureSensor(TypedDict):
    """Temperature sensor information.

    Attributes:
        sensorNum: Temperature sensor SKU
        sensorDesc: Description of the sensor (MAC-A, MAC-B, System)
        sensorTemp: Temperature in Celsius
        sensorState: Sensor operational state:
            0 = NONE
            1 = NORMAL
            2 = WARNING
            3 = CRITICAL
            4 = SHUTDOWN
            5 = NOT PRESENT
            6 = NOT OPERATIONAL
    """

    sensorNum: int
    sensorDesc: str
    sensorTemp: int
    sensorState: Literal[0, 1, 2, 3, 4, 5, 6]

class DeviceInfo(TypedDict):
    """Device information and status.

    Attributes:
        serialNumber: Switch Serial Number
        macAddr: Switch MAC Address (XX:XX:XX:XX:XX:XX format)
        model: Switch Model Number
        swVer: Active firmware version
        numOfPorts: Total number of switch ports available
        numOfActivePorts: Total number of currently active switch ports
        memoryUsage: Percentage of memory usage (e.g., "90.58%")
        cpuUsage: Percentage of CPU usage (e.g., "17.53%")
        fanState: List of fan status dictionaries (e.g., [{"FAN-1": "Operational"}])
        poeState: PoE enabled status
        upTime: Up time of device (e.g., "00 Days 01 Hrs 07 Mins 11 Secs")
        temperatureSensors: List of temperature sensor readings
        bootVersion: Bootcode version of the Switch
        rxData: Total number of bytes received
        txData: Total number of bytes transmitted
    """

    serialNumber: str
    macAddr: str
    model: str
    swVer: str
    numOfPorts: int
    numOfActivePorts: int
    memoryUsage: str
    cpuUsage: str
    fanState: List[Dict[str, str]]
    poeState: bool
    upTime: str
    temperatureSensors: List[TemperatureSensor]
    bootVersion: str
    rxData: int
    txData: int

# Type alias for device info endpoint response
DeviceInfoResult = ApiResult[DeviceInfo]

def get_device_info(base_url: str, token: str) -> DeviceInfoResult:
    """Get device information from M4300 switch.

    Args:
        base_url: Base URL of the API (e.g., https://192.168.99.92:8443)
        token: Authentication token from login

    Returns:
        Dictionary containing device information and status:
        {
            "data": {
                "serialNumber": str,
                "macAddr": str,
                "model": str,
                "swVer": str,
                "numOfPorts": int,
                "numOfActivePorts": int,
                "memoryUsage": str,
                "cpuUsage": str,
                "fanState": [{"FAN-1": str, ...}],
                "poeState": bool,
                "upTime": str,
                "temperatureSensors": [{
                    "sensorNum": int,
                    "sensorDesc": str,
                    "sensorTemp": int,
                    "sensorState": int
                }],
                "bootVersion": str,
                "rxData": int,
                "txData": int
            },
            "resp": {
                "status": str,
                "respCode": int,
                "respMsg": str
            }
        }

    Raises:
        ValueError: If required parameters are missing
        RuntimeError: If request fails or returns invalid response
    """
    # Validate required parameters
    if not base_url:
        raise ValueError("base_url is required")
    if not token:
        raise ValueError("token is required")

    # Prepare request
    url = f"{base_url}/api/v1/device_info"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}

    # Send request
    try:
        # SSL verification disabled for M4300's self-signed certificates
        response = requests.get(
            url,
            headers=headers,
            verify=False,  # nosec B501 - M4300 uses self-signed certificates
            timeout=DEFAULT_TIMEOUT,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise RuntimeError("Device info failed: Invalid token")
            raise RuntimeError(f"Device info failed: {str(e)}")

        # Parse response
        data = response.json()

        # Validate response format
        if not isinstance(data, dict):
            raise RuntimeError("Device info failed: Invalid response type")

        if "resp" not in data:
            raise RuntimeError("Device info failed: Missing response data")

        # Check if resp is None or not a dict
        if not isinstance(data["resp"], dict):
            raise RuntimeError("Device info failed: Invalid response format")

        if "status" not in data["resp"]:
            raise RuntimeError("Device info failed: Missing status")

        # Check error response before deviceInfo validation
        if data["resp"]["status"] != "success":
            msg = data["resp"].get("respMsg", "Unknown error")
            raise RuntimeError(f"Device info failed: {msg}")

        if "deviceInfo" not in data:
            raise RuntimeError("Device info failed: Missing device info")

        # Check if deviceInfo is None or not a dict
        if not isinstance(data["deviceInfo"], dict):
            raise RuntimeError("Device info failed: Invalid response format")

        # Validate required deviceInfo fields
        required_fields = {
            "serialNumber": str,
            "macAddr": str,
            "model": str,
            "swVer": str,
            "numOfPorts": int,
            "numOfActivePorts": int,
            "memoryUsage": str,
            "cpuUsage": str,
            "fanState": list,
            "poeState": bool,
            "upTime": str,
            "temperatureSensors": list,
            "bootVersion": str,
            "rxData": int,
            "txData": int,
        }

        device_info = data["deviceInfo"]
        for field, expected_type in required_fields.items():
            if field not in device_info:
                raise RuntimeError(f"Device info failed: Missing {field}")
            if not isinstance(device_info[field], expected_type):
                raise RuntimeError(f"Device info failed: Invalid {field} type")

        # Cast response to correct type
        return DeviceInfoResult(
            data=DeviceInfo(
                serialNumber=device_info["serialNumber"],
                macAddr=device_info["macAddr"],
                model=device_info["model"],
                swVer=device_info["swVer"],
                numOfPorts=device_info["numOfPorts"],
                numOfActivePorts=device_info["numOfActivePorts"],
                memoryUsage=device_info["memoryUsage"],
                cpuUsage=device_info["cpuUsage"],
                fanState=device_info["fanState"],
                poeState=device_info["poeState"],
                upTime=device_info["upTime"],
                temperatureSensors=device_info["temperatureSensors"],
                bootVersion=device_info["bootVersion"],
                rxData=device_info["rxData"],
                txData=device_info["txData"],
            ),
            resp=ResponseData(
                status=data["resp"]["status"],
                respCode=data["resp"]["respCode"],
                respMsg=data["resp"]["respMsg"],
            ),
        )

    except json.JSONDecodeError:
        raise RuntimeError("Device info failed: Invalid JSON response")
    except RequestException:
        raise RuntimeError("Device info failed: Connection error")
