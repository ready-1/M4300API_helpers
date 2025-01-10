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

# Default timeout for API requests (in seconds)
DEFAULT_TIMEOUT = 10

# Temperature sensor states
SensorState = Literal[0, 1, 2, 3, 4, 5, 6]
SENSOR_STATES = {
    0: "NONE",
    1: "NORMAL",
    2: "WARNING",
    3: "CRITICAL",
    4: "SHUTDOWN",
    5: "NOT PRESENT",
    6: "NOT OPERATIONAL"
}

class TemperatureSensor(TypedDict):
    """Temperature sensor information.
    
    Attributes:
        sensorNum: Temperature sensor SKU
        sensorDesc: Description of the temperature sensor
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
    sensorState: SensorState

class DeviceInfo(TypedDict):
    """Device information and status.
    
    Attributes:
        serialNumber: Switch Serial Number
        macAddr: Switch MAC Address
        model: Switch Model Number
        swVer: Active firmware version
        numOfPorts: Total number of switch ports available
        numOfActivePorts: Total number of currently active switch ports
        memoryUsage: Percentage of memory usage (e.g., "90.58%")
        cpuUsage: Percentage of CPU usage (e.g., "17.53%")
        fanState: Dictionary of fan names to states (e.g., {"FAN-1": "Operational"})
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

class ResponseData(TypedDict):
    """Standard API response data.
    
    Attributes:
        status: Response status ("success" or "failure")
        respCode: Response code (0 for success)
        respMsg: Human-readable response message
    """
    status: Literal["success", "failure"]
    respCode: int
    respMsg: str

class DeviceInfoResult(TypedDict):
    """Complete device info API response.
    
    Attributes:
        deviceInfo: Device information and status
        resp: Response status information
    """
    deviceInfo: DeviceInfo
    resp: ResponseData

def get_device_info(base_url: str, token: str) -> DeviceInfoResult:
    """Get device information from M4300 switch.
    
    Args:
        base_url: Base URL of the API (e.g., https://192.168.99.92:8443)
        token: Authentication token from login
        
    Returns:
        Dictionary containing device information and status:
        {
            "deviceInfo": {
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
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Send request
    try:
        # SSL verification disabled for M4300's self-signed certificates
        response = requests.get(
            url,
            headers=headers,
            verify=False,  # nosec B501 - M4300 uses self-signed certificates
            timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        
        try:
            # Parse response
            data = response.json()
            
            # Validate response format
            if not isinstance(data, dict):
                raise RuntimeError("Device info failed: Invalid response type")
            
            if "resp" not in data:
                raise RuntimeError("Device info failed: Missing response data")
                
            if "status" not in data["resp"]:
                raise RuntimeError("Device info failed: Missing status")
                
            # Check for error response
            if data["resp"]["status"] != "success":
                msg = data["resp"].get("respMsg", "Unknown error")
                raise RuntimeError(f"Device info failed: {msg}")
                
            # Cast response to correct type
            return DeviceInfoResult(
                deviceInfo=DeviceInfo(data["deviceInfo"]),
                resp=ResponseData(
                    status=data["resp"]["status"],
                    respCode=data["resp"]["respCode"],
                    respMsg=data["resp"]["respMsg"]
                )
            )
            
        except json.JSONDecodeError as e:
            raise RuntimeError("Device info failed: Invalid JSON response")
        except (KeyError, TypeError) as e:
            raise RuntimeError("Device info failed: Invalid response format")
            
    except RequestException as e:
        raise RuntimeError(f"Device info failed: {str(e)}")
