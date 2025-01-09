"""Integration tests for login endpoint against live M4300 switch."""
import pytest
from src.login.login import login

# Test switch configuration
TEST_SWITCH = {
    "base_url": "https://192.168.99.92:8443",
    "username": "admin",
    "password": "password123"
}

def test_live_login_success():
    """Test successful login with valid credentials on live switch."""
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

def test_live_login_invalid_password():
    """Test login failure with invalid password on live switch."""
    with pytest.raises(RuntimeError, match="Login failed:"):
        login(
            TEST_SWITCH["base_url"],
            TEST_SWITCH["username"],
            "wrong_password"
        )

def test_live_login_invalid_username():
    """Test login failure with invalid username on live switch."""
    with pytest.raises(RuntimeError, match="Login failed:"):
        login(
            TEST_SWITCH["base_url"],
            "invalid_user",
            TEST_SWITCH["password"]
        )

def test_live_login_invalid_url():
    """Test connection failure with invalid URL."""
    with pytest.raises(RuntimeError, match="API request failed:"):
        login(
            "https://192.168.99.92:9999",
            TEST_SWITCH["username"],
            TEST_SWITCH["password"]
        )
