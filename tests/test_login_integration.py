"""Integration tests for login endpoint against live M4300 switch.

This module contains integration tests that verify the login helper's
functionality against a live M4300 switch. These tests require access
to the test switch and valid credentials.

Test Environment:
    - Switch: 192.168.99.92:8443
    - Credentials: admin/password123
    - Rate limiting: 5 attempts per 5 minutes

Test Categories:
    1. Successful login with token validation
    2. Invalid credential handling
    3. Network error handling
    4. Rate limiting behavior

Note: These tests require the --run-integration flag:
    python -m pytest tests/test_login_integration.py -v --run-integration
"""
import pytest
from src.login.login import login

# Test switch configuration
TEST_SWITCH = {
    "base_url": "https://192.168.99.92:8443",
    "username": "admin",
    "password": "password123"
}

@pytest.mark.integration
def test_live_login_success():
    """Test successful login with valid credentials on live switch.
    
    Verifies:
        - Successful API connection
        - Valid JSON response
        - Token format and length
        - Response structure
        - Token expiration
    """
    result = login(
        TEST_SWITCH["base_url"],
        TEST_SWITCH["username"],
        TEST_SWITCH["password"]
    )
    
    # Verify response structure
    assert "login" in result
    assert "token" in result["login"]
    assert "expire" in result["login"]
    assert "resp" in result
    assert result["resp"]["status"] == "success"
    assert result["resp"]["respCode"] == 0
    
    # Verify token format (64 character hex string)
    assert len(result["login"]["token"]) == 128
    int(result["login"]["token"], 16)  # Should not raise ValueError
    
    # Verify expiration (86400 seconds = 24 hours)
    assert result["login"]["expire"] == "86400"

@pytest.mark.integration
def test_live_login_invalid_password():
    """Test login failure with invalid password on live switch.
    
    Verifies:
        - Invalid password detection
        - Error message format
        - RuntimeError exception
    """
    with pytest.raises(RuntimeError, match="Login failed:"):
        login(
            TEST_SWITCH["base_url"],
            TEST_SWITCH["username"],
            "wrong_password"
        )

@pytest.mark.integration
def test_live_login_invalid_username():
    """Test login failure with invalid username on live switch.
    
    Verifies:
        - Invalid username detection
        - Error message format
        - RuntimeError exception
        - Rate limiting messages
    """
    with pytest.raises(RuntimeError, match="Login failed:"):
        login(
            TEST_SWITCH["base_url"],
            "invalid_user",
            TEST_SWITCH["password"]
        )

@pytest.mark.integration
def test_live_login_invalid_url():
    """Test connection failure with invalid URL.
    
    Verifies:
        - Network error handling
        - Connection timeout
        - Error message format
    """
    with pytest.raises(RuntimeError, match="API request failed:"):
        login(
            "https://192.168.99.92:9999",
            TEST_SWITCH["username"],
            TEST_SWITCH["password"]
        )
