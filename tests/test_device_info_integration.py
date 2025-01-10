"""Integration tests for device info helper module."""

import pytest
from m4300api_helpers.login import login
from m4300api_helpers.device_info import get_device_info


@pytest.fixture
def auth_token(switch_config):
    """Fixture to get valid auth token for testing."""
    result = login(
        switch_config["base_url"], switch_config["username"], switch_config["password"]
    )
    return result["data"]["token"]


@pytest.mark.integration
def test_live_device_info_success(switch_config, auth_token):
    """Test successful device info retrieval with valid token on live switch.

    Verifies:
        - Successful API connection
        - Valid JSON response
        - Response structure
        - Required fields
        - Field types
    """
    result = get_device_info(switch_config["base_url"], auth_token)

    # Verify response structure
    assert "data" in result
    assert "resp" in result
    assert result["resp"]["status"] == "success"
    assert result["resp"]["respCode"] == 0

    # Verify required fields
    device_info = result["data"]
    assert "serialNumber" in device_info
    assert "macAddr" in device_info
    assert "model" in device_info
    assert "swVer" in device_info
    assert "numOfPorts" in device_info
    assert "numOfActivePorts" in device_info
    assert "memoryUsage" in device_info
    assert "cpuUsage" in device_info
    assert "fanState" in device_info
    assert "poeState" in device_info
    assert "upTime" in device_info
    assert "temperatureSensors" in device_info
    assert "bootVersion" in device_info
    assert "rxData" in device_info
    assert "txData" in device_info

    # Verify field types
    assert isinstance(device_info["serialNumber"], str)
    assert isinstance(device_info["macAddr"], str)
    assert isinstance(device_info["model"], str)
    assert isinstance(device_info["swVer"], str)
    assert isinstance(device_info["numOfPorts"], int)
    assert isinstance(device_info["numOfActivePorts"], int)
    assert isinstance(device_info["memoryUsage"], str)
    assert isinstance(device_info["cpuUsage"], str)
    assert isinstance(device_info["fanState"], list)
    assert isinstance(device_info["poeState"], bool)
    assert isinstance(device_info["upTime"], str)
    assert isinstance(device_info["temperatureSensors"], list)
    assert isinstance(device_info["bootVersion"], str)
    assert isinstance(device_info["rxData"], int)
    assert isinstance(device_info["txData"], int)


@pytest.mark.integration
def test_live_device_info_expired_token(switch_config):
    """Test device info with expired token on live switch.

    Verifies:
        - Error handling
        - Error message format
        - RuntimeError exception
    """
    expired_token = "expired_token_123"
    with pytest.raises(RuntimeError, match="Device info failed: Invalid token"):
        get_device_info(switch_config["base_url"], expired_token)


@pytest.mark.integration
def test_live_device_info_invalid_url(switch_config, auth_token):
    """Test device info with invalid URL on live switch.

    Verifies:
        - Error handling
        - Error message format
        - RuntimeError exception
    """
    with pytest.raises(RuntimeError, match="Device info failed: Connection error"):
        get_device_info("https://invalid.url:8443", auth_token)
