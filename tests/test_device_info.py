"""Unit tests for device info endpoint helper.

This module contains unit tests for the device info helper functionality.
These tests use mocked responses to verify behavior without requiring
access to a live switch.

Test Categories:
    1. Successful device info response handling
    2. Input parameter validation
    3. Error response handling
    4. Network error handling
    5. Response format validation
"""
import json
import pytest
import requests
from requests.exceptions import RequestException
from m4300api_helpers.device_info.device_info import get_device_info, DEFAULT_TIMEOUT

@pytest.fixture
def test_token():
    """Fixture providing a test token."""
    return "8c523ad44e0a8f46324aa71f371963e07211b04b7239519a6f60f1ee5939dcc0"

@pytest.fixture
def mock_success_response():
    """Fixture providing a successful device info response."""
    return {
        "deviceInfo": {
            "serialNumber": "53L69C5FF001D",
            "macAddr": "BC:A5:11:A0:7E:1D",
            "model": "M4300-52G-PoE+",
            "swVer": "12.0.19.6",
            "numOfPorts": 52,
            "numOfActivePorts": 1,
            "memoryUsage": "90.58%",
            "cpuUsage": "17.53%",
            "fanState": [{
                "FAN-1": "Operational",
                "FAN-2": "Operational",
                "FAN-3": "Operational",
                "FAN-4": "Operational"
            }],
            "poeState": True,
            "upTime": "00 Days 01 Hrs 07 Mins 11 Secs",
            "temperatureSensors": [{
                "sensorNum": 1,
                "sensorDesc": "MAC-A",
                "sensorTemp": 23,
                "sensorState": 1
            }, {
                "sensorNum": 2,
                "sensorDesc": "MAC-B",
                "sensorTemp": 31,
                "sensorState": 1
            }],
            "bootVersion": "B1.0.0.17",
            "rxData": 9269183,
            "txData": 2814740
        },
        "resp": {
            "status": "success",
            "respCode": 0,
            "respMsg": "Operation success"
        }
    }

def test_successful_device_info(mocker, switch_config, test_token, mock_success_response):
    """Test successful device info retrieval with mocked response.
    
    Verifies:
        - Request format
        - Header validation
        - Response parsing
        - Return value structure
        - Type casting
    """
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = mock_success_response
    mock_get.return_value.raise_for_status.return_value = None
    
    result = get_device_info(switch_config["base_url"], test_token)
    
    assert result == mock_success_response
    mock_get.assert_called_once_with(
        f"{switch_config['base_url']}/api/v1/device_info",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {test_token}"
        },
        verify=False,
        timeout=DEFAULT_TIMEOUT
    )

def test_missing_base_url(test_token):
    """Test error handling for missing base URL.
    
    Verifies:
        - Input validation
        - Error message format
        - ValueError exception
    """
    with pytest.raises(ValueError, match="base_url is required"):
        get_device_info("", test_token)

def test_missing_token(switch_config):
    """Test error handling for missing token.
    
    Verifies:
        - Input validation
        - Error message format
        - ValueError exception
    """
    with pytest.raises(ValueError, match="token is required"):
        get_device_info(switch_config["base_url"], "")

def test_failed_device_info(mocker, switch_config, test_token):
    """Test handling of failed device info request.
    
    Verifies:
        - Error response parsing
        - Error message format
        - RuntimeError exception
    """
    mock_response = {
        "resp": {
            "status": "failure",
            "respCode": 1,
            "respMsg": "Invalid token"
        }
    }
    
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Device info failed: Invalid token"):
        get_device_info(switch_config["base_url"], "invalid_token")

def test_invalid_response_type(mocker, switch_config, test_token):
    """Test handling of non-dict response.
    
    Verifies:
        - Response type validation
        - Error message format
        - RuntimeError exception
    """
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = ["not", "a", "dict"]
    mock_get.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Device info failed: Invalid response type"):
        get_device_info(switch_config["base_url"], test_token)

def test_missing_resp_field(mocker, switch_config, test_token):
    """Test handling of missing resp field.
    
    Verifies:
        - Response structure validation
        - Error message format
        - RuntimeError exception
    """
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = {"deviceInfo": {}}
    mock_get.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Device info failed: Missing response data"):
        get_device_info(switch_config["base_url"], test_token)

def test_invalid_response_format(mocker, switch_config, test_token):
    """Test handling of invalid response format.
    
    Verifies:
        - Response validation
        - Error message format
        - RuntimeError exception
    """
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = {"resp": {}}
    mock_get.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Device info failed: Missing status"):
        get_device_info(switch_config["base_url"], test_token)

def test_request_exception(mocker, switch_config, test_token):
    """Test handling of request exception.
    
    Verifies:
        - Network error handling
        - Error message format
        - RuntimeError exception
    """
    mock_get = mocker.patch('requests.get')
    mock_get.side_effect = RequestException("Connection error")
    
    with pytest.raises(RuntimeError, match="Device info failed: Connection error"):
        get_device_info(switch_config["base_url"], test_token)

def test_invalid_json_response(mocker, switch_config, test_token):
    """Test handling of invalid JSON response.
    
    Verifies:
        - JSON parsing error handling
        - Error message format
        - RuntimeError exception
    """
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_get.return_value.text = "Invalid JSON response"
    mock_get.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Device info failed: Invalid JSON response"):
        get_device_info(switch_config["base_url"], test_token)
