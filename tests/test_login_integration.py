"""Integration tests for login endpoint against live M4300 switch.

This module contains integration tests that verify the login helper's
functionality against a live M4300 switch. These tests require access
to the test switch and valid credentials.

Test Environment:
    - Switch configuration from environment variables
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
from m4300api_helpers.login.login import login

@pytest.mark.integration
def test_live_login_success(switch_config):
    """Test successful login with valid credentials on live switch.
    
    Verifies:
        - Successful API connection
        - Valid JSON response
        - Token format and length
        - Response structure
        - Token expiration
    """
    result = login(
        switch_config["base_url"],
        switch_config["username"],
        switch_config["password"]
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
def test_live_login_invalid_password(switch_config):
    """Test login failure with invalid password on live switch.
    
    Verifies:
        - Invalid password detection
        - Error message format
        - RuntimeError exception
    """
    with pytest.raises(RuntimeError, match="Login failed:"):
        login(
            switch_config["base_url"],
            switch_config["username"],
            "wrong_password"
        )

@pytest.mark.integration
def test_live_login_invalid_username(switch_config):
    """Test login failure with invalid username on live switch.
    
    Verifies:
        - Invalid username detection
        - Error message format
        - RuntimeError exception
        - Rate limiting messages
    """
    with pytest.raises(RuntimeError, match="Login failed:"):
        login(
            switch_config["base_url"],
            "invalid_user",
            switch_config["password"]
        )

@pytest.mark.integration
def test_live_login_invalid_url(switch_config):
    """Test connection failure with invalid URL.
    
    Verifies:
        - Network error handling
        - Connection timeout
        - Error message format
    """
    # Modify port to create invalid URL
    base_url = switch_config["base_url"].replace(":8443", ":9999")
    with pytest.raises(RuntimeError, match="API request failed:"):
        login(
            base_url,
            switch_config["username"],
            switch_config["password"]
        )
