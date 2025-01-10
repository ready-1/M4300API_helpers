"""Integration tests for login helper module."""

import pytest
from m4300api_helpers.login import login


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
    assert "data" in result
    assert "resp" in result
    assert "token" in result["data"]
    assert "expire" in result["data"]
    assert result["resp"]["status"] == "success"
    assert result["resp"]["respCode"] == 0
    
    # Verify token format
    token = result["data"]["token"]
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Verify expiration
    expire = result["data"]["expire"]
    assert expire == "86400"  # 24 hours in seconds


@pytest.mark.integration
def test_live_login_invalid_password(switch_config):
    """Test login with invalid password on live switch.
    
    Verifies:
        - Error handling
        - Error message format
        - RuntimeError exception
    """
    with pytest.raises(RuntimeError, match="Login failed: Invalid credentials"):
        login(switch_config["base_url"], switch_config["username"], "wrong_password")


@pytest.mark.integration
def test_live_login_invalid_username(switch_config):
    """Test login with invalid username on live switch.
    
    Verifies:
        - Error handling
        - Error message format
        - RuntimeError exception
    """
    with pytest.raises(RuntimeError, match="Login failed: Invalid credentials"):
        login(switch_config["base_url"], "invalid_user", switch_config["password"])


@pytest.mark.integration
def test_live_login_invalid_url(switch_config):
    """Test login with invalid URL on live switch.
    
    Verifies:
        - Error handling
        - Error message format
        - RuntimeError exception
    """
    with pytest.raises(RuntimeError, match="API request failed"):
        login(
            "https://invalid.url:8443",
            switch_config["username"],
            switch_config["password"]
        )
