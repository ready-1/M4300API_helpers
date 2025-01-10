"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def switch_config():
    """Test switch configuration.

    Returns:
        Dictionary containing test switch configuration:
        {
            "base_url": str,  # Base URL of test switch
            "username": str,  # Admin username
            "password": str   # Admin password
        }
    """
    return {
        "base_url": "https://192.168.99.92:8443",
        "username": "admin",
        "password": "password123",
    }


@pytest.fixture
def test_token():
    """Test authentication token.

    Returns:
        String containing test authentication token
    """
    return "8c523ad44e0a8f46324aa71f371963e07211b04b7239519a6f60f1ee5939dcc0"


@pytest.fixture
def mock_success_response():
    """Mock successful device info response.

    Returns:
        Dictionary containing mock device info response
    """
    return {
        "deviceInfo": {
            "serialNumber": "123456789",
            "macAddr": "BC:A5:11:A0:7E:1D",
            "model": "M4300-96X",
            "swVer": "12.0.4.4",
            "numOfPorts": 96,
            "numOfActivePorts": 48,
            "memoryUsage": "90.58%",
            "cpuUsage": "17.53%",
            "fanState": [{"FAN-1": "Operational", "FAN-2": "Operational"}],
            "poeState": True,
            "upTime": "00 Days 01 Hrs 07 Mins 11 Secs",
            "temperatureSensors": [
                {
                    "sensorNum": 1,
                    "sensorDesc": "MAC-A",
                    "sensorTemp": 45,
                    "sensorState": 1,
                },
                {
                    "sensorNum": 2,
                    "sensorDesc": "MAC-B",
                    "sensorTemp": 48,
                    "sensorState": 1,
                },
                {
                    "sensorNum": 3,
                    "sensorDesc": "System",
                    "sensorTemp": 42,
                    "sensorState": 1,
                },
            ],
            "bootVersion": "B1.0.0.17",
            "rxData": 123456789,
            "txData": 987654321,
        },
        "resp": {"status": "success", "respCode": 0, "respMsg": "Operation success"},
    }
