"""Test fixtures for API responses."""

from typing import Dict, Any

# Authentication responses
LOGIN_SUCCESS: Dict[str, Any] = {
    "resp": {
        "status": "success",
        "respCode": 0,
        "respMsg": "Operation success"
    },
    "login": {
        "token": "example-token-12345",
        "expires": 3600
    }
}

LOGIN_FAILURE: Dict[str, Any] = {
    "resp": {
        "status": "failure",
        "respCode": 401,
        "respMsg": "Invalid credentials"
    }
}

# Device information responses
DEVICE_INFO_SUCCESS: Dict[str, Any] = {
    "resp": {
        "status": "success",
        "respCode": 0,
        "respMsg": "Operation success"
    },
    "device_info": {
        "name": "Test Switch",
        "serialNumber": "123456789",
        "macAddr": "00:11:22:33:44:55",
        "model": "M4300-48X",
        "lanIpAddress": "192.168.1.1",
        "swVer": "12.0.0.1",
        "lastReboot": "2023-01-01 00:00:00",
        "numOfPorts": 48,
        "numOfActivePorts": 24,
        "rstpState": True,
        "memoryUsed": "512MB",
        "memoryUsage": "50%",
        "cpuUsage": "10%",
        "fanState": "active",
        "poeState": True,
        "upTime": "10 days",
        "temperatureSensors": [
            {
                "sensorNum": 1,
                "sensorDesc": "Main",
                "sensorTemp": "45C",
                "sensorState": 1
            }
        ],
        "bootVersion": "1.0.0",
        "rxData": 1000000,
        "txData": 2000000,
        "adminPoePower": 1000
    }
}

DEVICE_INFO_FAILURE: Dict[str, Any] = {
    "resp": {
        "status": "failure",
        "respCode": 500,
        "respMsg": "Internal error"
    }
}

# VLAN responses
VLAN_CONFIG_SUCCESS: Dict[str, Any] = {
    "resp": {
        "status": "success",
        "respCode": 0,
        "respMsg": "Operation success"
    },
    "switchConfigVlan": {
        "vlanId": 100,
        "name": "Engineering",
        "voiceVlanState": False,
        "autoVoipState": False,
        "autoVideoState": False,
        "igmpConfig": {
            "igmpState": False
        }
    }
}

VLAN_CONFIG_FAILURE: Dict[str, Any] = {
    "resp": {
        "status": "failure",
        "respCode": 400,
        "respMsg": "Invalid VLAN ID"
    }
}

# Error responses
TOKEN_EXPIRED: Dict[str, Any] = {
    "resp": {
        "status": "failure",
        "respCode": 401,
        "respMsg": "Token expired"
    }
}

RATE_LIMIT_EXCEEDED: Dict[str, Any] = {
    "resp": {
        "status": "failure",
        "respCode": 429,
        "respMsg": "Rate limit exceeded"
    }
}
