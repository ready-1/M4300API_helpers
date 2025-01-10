"""Integration tests for logout helper module."""

import pytest
from m4300api_helpers.login import login
from m4300api_helpers.logout import logout


@pytest.fixture
def auth_token(switch_config):
    """Fixture to get valid auth token for testing."""
    print(f"\nswitch_config type: {type(switch_config)}")
    print(f"switch_config keys: {switch_config.keys()}")
    print(f"switch_config: {switch_config}")
    result = login(
        switch_config["base_url"], switch_config["username"], switch_config["password"]
    )
    return result["data"]["token"]


@pytest.mark.integration
def test_live_logout_success(switch_config, auth_token):
    """Test successful logout with valid token on live switch.

    Verifies:
        - Successful API connection
        - Valid JSON response
        - Response structure
        - Token invalidation
    """
    result = logout(switch_config["base_url"], auth_token)

    # Verify response structure
    assert "data" in result
    assert "resp" in result
    assert result["data"] == {}  # Empty object as specified in API
    assert result["resp"]["status"] == "success"
    assert result["resp"]["respCode"] == 0


@pytest.mark.integration
def test_live_logout_expired_token(switch_config):
    """Test logout with expired token on live switch.

    Verifies:
        - Error handling
        - Error message format
        - RuntimeError exception
    """
    expired_token = "expired_token_123"
    with pytest.raises(RuntimeError, match="Logout failed: Invalid token"):
        logout(switch_config["base_url"], expired_token)


@pytest.mark.integration
def test_live_logout_invalid_url(switch_config, auth_token):
    """Test logout with invalid URL on live switch.

    Verifies:
        - Error handling
        - Error message format
        - RuntimeError exception
    """
    with pytest.raises(RuntimeError, match="Logout failed: Connection error"):
        logout("https://invalid.url:8443", auth_token)


@pytest.mark.integration
def test_live_logout_double_logout(switch_config, auth_token):
    """Test double logout with same token on live switch.

    Verifies:
        - Error handling
        - Error message format
        - RuntimeError exception
    """
    # First logout should succeed
    logout(switch_config["base_url"], auth_token)

    # Second logout should fail with invalid token
    with pytest.raises(RuntimeError, match="Logout failed: Invalid token"):
        logout(switch_config["base_url"], auth_token)
