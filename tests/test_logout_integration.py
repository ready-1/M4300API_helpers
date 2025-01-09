"""Integration tests for logout endpoint against live M4300 switch.

This module contains integration tests that verify the logout helper's
functionality against a live M4300 switch. These tests require access
to the test switch and valid credentials.

Test Environment:
    - Switch configuration from environment variables
    - Rate limiting: 5 attempts per 5 minutes

Test Categories:
    1. Successful logout with token validation
    2. Invalid token handling
    3. Network error handling
    4. Token reuse prevention

Note: These tests require the --run-integration flag:
    python -m pytest tests/test_logout_integration.py -v --run-integration
"""
import pytest
from m4300api_helpers.login.login import login
from m4300api_helpers.logout.logout import logout

@pytest.fixture
def auth_token(switch_config):
    """Fixture to get valid auth token for testing."""
    print(f"\nswitch_config type: {type(switch_config)}")
    print(f"switch_config keys: {switch_config.keys()}")
    print(f"switch_config: {switch_config}")
    result = login(
        switch_config["base_url"],
        switch_config["username"],
        switch_config["password"]
    )
    return result["login"]["token"]

@pytest.mark.integration
def test_live_logout_success(auth_token, switch_config):
    """Test successful logout with valid token on live switch.
    
    Verifies:
        - Successful API connection
        - Valid JSON response
        - Response structure
        - Token invalidation
    """
    result = logout(
        switch_config["base_url"],
        auth_token
    )
    
    # Verify response structure
    assert "logout" in result
    assert "resp" in result
    assert result["resp"]["status"] == "success"
    assert result["resp"]["respCode"] == 0
    
    # Verify token is invalidated by attempting reuse
    with pytest.raises(RuntimeError, match="Logout failed:"):
        logout(switch_config["base_url"], auth_token)

@pytest.mark.integration
def test_live_logout_invalid_token(switch_config):
    """Test logout failure with invalid token on live switch.
    
    Verifies:
        - Invalid token detection
        - Error message format
        - RuntimeError exception
    """
    with pytest.raises(RuntimeError, match="Logout failed:"):
        logout(
            switch_config["base_url"],
            "invalid_token_123"
        )

@pytest.mark.integration
def test_live_logout_expired_token(auth_token, switch_config):
    """Test logout with already logged out token.
    
    Verifies:
        - Expired token detection
        - Error message format
        - RuntimeError exception
    """
    # First logout to invalidate token
    logout(switch_config["base_url"], auth_token)
    
    # Attempt to reuse invalidated token
    with pytest.raises(RuntimeError, match="Logout failed:"):
        logout(switch_config["base_url"], auth_token)

@pytest.mark.integration
def test_live_logout_invalid_url(auth_token, switch_config):
    """Test connection failure with invalid URL.
    
    Verifies:
        - Network error handling
        - Connection timeout
        - Error message format
    """
    # Modify port to create invalid URL
    base_url = switch_config["base_url"].replace(":8443", ":9999")
    with pytest.raises(RuntimeError, match="Logout failed:"):
        logout(base_url, auth_token)
