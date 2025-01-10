"""Integration tests for device info endpoint against live M4300 switch.

This module contains integration tests that verify the device info helper's
functionality against a live M4300 switch. These tests require access
to the test switch and valid credentials.

Test Environment:
    - Switch configuration from environment variables
    - Rate limiting: 5 attempts per 5 minutes

Test Categories:
    1. Successful device info retrieval
    2. Invalid token handling
    3. Network error handling
    4. Response validation

Note: These tests require the --run-integration flag:
    python -m pytest tests/test_device_info_integration.py -v --run-integration
"""
import pytest
from m4300api_helpers.login.login import login
from m4300api_helpers.device_info.device_info import get_device_info

@pytest.fixture
def auth_token(switch_config):
    """Fixture to get valid auth token for testing."""
    result = login(
        switch_config["base_url"],
        switch_config["username"],
        switch_config["password"]
    )
    return result["login"]["token"]

@pytest.mark.integration
def test_live_device_info_success(auth_token, switch_config):
    """Test successful device info retrieval from live switch.
    
    Verifies:
        - Successful API connection
        - Valid JSON response
        - Response structure
        - Data types
    """
    result = get_device_info(
        switch_config["base_url"],
        auth_token
    )
    
    # Verify response structure
    assert "deviceInfo" in result
    assert "resp" in result
    assert result["resp"]["status"] == "success"
    assert result["resp"]["respCode"] == 0
    
    # Verify device info fields
    device_info = result["deviceInfo"]
    
    # Verify serial number format (e.g., "53L69C5FF001D")
    assert len(device_info["serialNumber"]) > 0
    assert device_info["serialNumber"].isalnum()  # Only letters and numbers
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
    
    # Verify fan state structure
    assert len(device_info["fanState"]) > 0
    fan_state = device_info["fanState"][0]
    for fan_name, fan_status in fan_state.items():
        assert fan_name.startswith("FAN-")
        assert fan_status in ["Operational", "Not Operational"]

    # Verify percentage formats
    assert device_info["memoryUsage"].endswith("%")
    assert float(device_info["memoryUsage"].rstrip("%")) >= 0
    assert float(device_info["memoryUsage"].rstrip("%")) <= 100
    
    assert device_info["cpuUsage"].endswith("%")
    assert float(device_info["cpuUsage"].rstrip("%")) >= 0
    assert float(device_info["cpuUsage"].rstrip("%")) <= 100

    # Verify MAC address format (XX:XX:XX:XX:XX:XX)
    mac_parts = device_info["macAddr"].split(":")
    assert len(mac_parts) == 6
    for part in mac_parts:
        assert len(part) == 2
        int(part, 16)  # Verify valid hex

    # Verify uptime format
    uptime = device_info["upTime"]
    assert "Days" in uptime
    assert "Hrs" in uptime
    assert "Mins" in uptime
    assert "Secs" in uptime
    parts = uptime.split()
    assert len(parts) == 8
    assert int(parts[0]) >= 0  # Days
    assert 0 <= int(parts[2]) <= 23  # Hours
    assert 0 <= int(parts[4]) <= 59  # Minutes
    assert 0 <= int(parts[6]) <= 59  # Seconds

    # Verify temperature sensors
    for sensor in device_info["temperatureSensors"]:
        assert isinstance(sensor["sensorNum"], int)
        assert isinstance(sensor["sensorDesc"], str)
        assert isinstance(sensor["sensorTemp"], int)
        assert isinstance(sensor["sensorState"], int)
        assert 0 <= sensor["sensorState"] <= 6
        assert 0 <= sensor["sensorTemp"] <= 100  # Reasonable temp range
        assert sensor["sensorDesc"] in ["MAC-A", "MAC-B", "System"]

@pytest.mark.integration
def test_live_device_info_invalid_token(switch_config):
    """Test device info failure with invalid token on live switch.
    
    Verifies:
        - Invalid token detection
        - Error message format
        - RuntimeError exception
    """
    with pytest.raises(RuntimeError, match="Device info failed:"):
        get_device_info(
            switch_config["base_url"],
            "invalid_token_123"
        )

@pytest.mark.integration
def test_live_device_info_expired_token(auth_token, switch_config):
    """Test device info with expired token.
    
    Verifies:
        - Expired token detection
        - Error message format
        - RuntimeError exception
    """
    # First logout to invalidate token
    from m4300api_helpers.logout.logout import logout
    logout(switch_config["base_url"], auth_token)
    
    # Attempt to use invalidated token
    with pytest.raises(RuntimeError, match="Device info failed:"):
        get_device_info(switch_config["base_url"], auth_token)

@pytest.mark.integration
def test_live_device_info_invalid_url(auth_token, switch_config):
    """Test connection failure with invalid URL.
    
    Verifies:
        - Network error handling
        - Connection timeout
        - Error message format
    """
    # Modify port to create invalid URL
    base_url = switch_config["base_url"].replace(":8443", ":9999")
    with pytest.raises(RuntimeError, match="Device info failed:"):
        get_device_info(base_url, auth_token)
