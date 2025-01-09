"""Integration tests for logout endpoint against live M4300 switch.

This module contains integration tests that verify the logout helper's
functionality against a live M4300 switch. These tests require access
to the test switch and valid credentials.

Test Environment:
    - Switch: 192.168.99.92:8443
    - Credentials: admin/password123
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
from src.login.login import login
from src.logout.logout import logout

# Test switch configuration
TEST_SWITCH = {
    "base_url": "https://192.168.99.92:8443",
    "username": "admin",
    "password": "password123"
}

@pytest.fixture
def auth_token():
    """Fixture to get valid auth token for testing."""
    result = login(
        TEST_SWITCH["base_url"],
        TEST_SWITCH["username"],
        TEST_SWITCH["password"]
    )
    return result["login"]["token"]

@pytest.mark.integration
def test_live_logout_success(auth_token):
    """Test successful logout with valid token on live switch.
    
    Verifies:
        - Successful API connection
        - Valid JSON response
        - Response structure
        - Token invalidation
    """
    result = logout(
        TEST_SWITCH["base_url"],
        auth_token
    )
    
    # Verify response structure
    assert "logout" in result
    assert "resp" in result
    assert result["resp"]["status"] == "success"
    assert result["resp"]["respCode"] == 0
    
    # Verify token is invalidated by attempting reuse
    with pytest.raises(RuntimeError, match="Logout failed:"):
        logout(TEST_SWITCH["base_url"], auth_token)

@pytest.mark.integration
def test_live_logout_invalid_token():
    """Test logout failure with invalid token on live switch.
    
    Verifies:
        - Invalid token detection
        - Error message format
        - RuntimeError exception
    """
    with pytest.raises(RuntimeError, match="Logout failed:"):
        logout(
            TEST_SWITCH["base_url"],
            "invalid_token_123"
        )

@pytest.mark.integration
def test_live_logout_expired_token(auth_token):
    """Test logout with already logged out token.
    
    Verifies:
        - Expired token detection
        - Error message format
        - RuntimeError exception
    """
    # First logout to invalidate token
    logout(TEST_SWITCH["base_url"], auth_token)
    
    # Attempt to reuse invalidated token
    with pytest.raises(RuntimeError, match="Logout failed:"):
        logout(TEST_SWITCH["base_url"], auth_token)

@pytest.mark.integration
def test_live_logout_invalid_url(auth_token):
    """Test connection failure with invalid URL.
    
    Verifies:
        - Network error handling
        - Connection timeout
        - Error message format
    """
    with pytest.raises(RuntimeError, match="API request failed:"):
        logout(
            "https://192.168.99.92:9999",
            auth_token
        )
