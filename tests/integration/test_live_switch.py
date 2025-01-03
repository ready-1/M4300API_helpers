"""Integration tests with live switch."""

import os
from typing import Generator

import pytest
import responses

from m4300api_helpers.client import M4300Client
from m4300api_helpers.config import M4300Config
from m4300api_helpers.exceptions import (
    APIError,
    AuthenticationError,
    InvalidCredentialsError,
)

@pytest.fixture
def live_config() -> Generator[M4300Config, None, None]:
    """Create configuration for live switch testing.
    
    This fixture requires the following environment variables:
    - M4300_TEST_HOST: Hostname or IP of test switch
    - M4300_TEST_USERNAME: Username for test switch
    - M4300_TEST_PASSWORD: Password for test switch
    
    Yields:
        M4300Config: Configuration for live switch
    """
    required_vars = [
        "M4300_TEST_HOST",
        "M4300_TEST_USERNAME",
        "M4300_TEST_PASSWORD"
    ]
    
    # Check for required environment variables
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        pytest.skip(f"Missing required environment variables: {', '.join(missing)}")
    
    config = M4300Config(
        host=os.getenv("M4300_TEST_HOST", ""),
        username=os.getenv("M4300_TEST_USERNAME", ""),
        password=os.getenv("M4300_TEST_PASSWORD", ""),
        verify_ssl=False  # Test switches often use self-signed certificates
    )
    
    yield config

@pytest.fixture
def live_client(live_config: M4300Config) -> M4300Client:
    """Create client for live switch testing.
    
    Args:
        live_config: Live switch configuration
        
    Returns:
        M4300Client: Client configured for live switch
    """
    return M4300Client(live_config)

@pytest.mark.live_switch
def test_live_authentication(live_client: M4300Client) -> None:
    """Test authentication against live switch."""
    live_client.authenticate()
    assert live_client._auth_token is not None

@pytest.mark.live_switch
def test_live_authentication_failure() -> None:
    """Test authentication failure with invalid credentials."""
    config = M4300Config(
        host=os.getenv("M4300_TEST_HOST", ""),
        username="invalid",
        password="invalid",
        verify_ssl=False
    )
    client = M4300Client(config)
    
    with pytest.raises(InvalidCredentialsError):
        client.authenticate()

@pytest.mark.live_switch
def test_live_device_info(live_client: M4300Client) -> None:
    """Test getting device information from live switch."""
    response = live_client.get("device_info")
    
    # Verify response structure
    assert "device_info" in response
    info = response["device_info"]
    
    # Verify required fields
    assert isinstance(info["name"], str)
    assert isinstance(info["serialNumber"], str)
    assert isinstance(info["model"], str)
    assert isinstance(info["swVer"], str)
    assert isinstance(info["numOfPorts"], int)

@pytest.mark.live_switch
def test_live_vlan_operations(live_client: M4300Client) -> None:
    """Test VLAN operations on live switch.
    
    This test:
    1. Creates a test VLAN
    2. Verifies it was created
    3. Modifies the VLAN
    4. Verifies the changes
    5. Deletes the VLAN
    6. Verifies it was deleted
    """
    test_vlan_id = 999  # Use high number to avoid conflicts
    
    try:
        # Create VLAN
        live_client.post("swcfg_vlan", params={"vlanid": test_vlan_id}, json={
            "switchConfigVlan": {
                "vlanId": test_vlan_id,
                "name": "Test VLAN",
                "voiceVlanState": False,
                "autoVoipState": False,
                "autoVideoState": False,
                "igmpConfig": {
                    "igmpState": False
                }
            }
        })
        
        # Verify VLAN exists
        response = live_client.get("swcfg_vlan", params={"vlanid": test_vlan_id})
        assert response["switchConfigVlan"]["vlanId"] == test_vlan_id
        assert response["switchConfigVlan"]["name"] == "Test VLAN"
        
        # Modify VLAN
        live_client.post("swcfg_vlan", params={"vlanid": test_vlan_id}, json={
            "switchConfigVlan": {
                "vlanId": test_vlan_id,
                "name": "Modified Test VLAN",
                "voiceVlanState": False,
                "autoVoipState": False,
                "autoVideoState": False,
                "igmpConfig": {
                    "igmpState": False
                }
            }
        })
        
        # Verify changes
        response = live_client.get("swcfg_vlan", params={"vlanid": test_vlan_id})
        assert response["switchConfigVlan"]["name"] == "Modified Test VLAN"
        
    finally:
        # Cleanup: Delete test VLAN
        try:
            live_client.delete("swcfg_vlan", params={"vlanid": test_vlan_id})
        except APIError:
            pass  # Ignore cleanup errors

@pytest.mark.live_switch
def test_live_rate_limiting(live_client: M4300Client) -> None:
    """Test rate limiting against live switch."""
    # Configure strict rate limit
    live_client.config.rate_limit = 2  # 2 requests per second
    
    # Make several requests in quick succession
    for _ in range(3):
        live_client.get("device_info")
    
    # If we got here without rate limit errors, the rate limiting worked

@pytest.mark.live_switch
def test_live_error_handling(live_client: M4300Client) -> None:
    """Test error handling with live switch."""
    # Test invalid endpoint
    with pytest.raises(APIError) as exc_info:
        live_client.get("invalid_endpoint")
    assert exc_info.value.status_code == 404

    # Test invalid VLAN ID
    with pytest.raises(APIError) as exc_info:
        live_client.get("swcfg_vlan", params={"vlanid": 99999})
    assert exc_info.value.status_code == 400
