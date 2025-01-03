"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from m4300api_helpers.config import M4300Config
from m4300api_helpers.exceptions import ConfigurationError

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "M4300_HOST": "switch.example.com",
        "M4300_USERNAME": "admin",
        "M4300_PASSWORD": "password123",
        "M4300_PORT": "8443",
        "M4300_VERIFY_SSL": "true",
        "M4300_TIMEOUT": "30",
        "M4300_RATE_LIMIT": "10",
        "M4300_TOKEN_REFRESH_MARGIN": "300"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

def test_config_from_env(mock_env_vars):
    """Test creating configuration from environment variables."""
    config = M4300Config.from_env()
    
    assert config.host == "switch.example.com"
    assert config.username == "admin"
    assert config.password == "password123"
    assert config.port == 8443
    assert config.verify_ssl is True
    assert config.timeout == 30
    assert config.rate_limit == 10
    assert config.token_refresh_margin == 300

def test_config_missing_required_env():
    """Test error when required environment variables are missing."""
    with pytest.raises(ConfigurationError) as exc_info:
        M4300Config.from_env()
    
    assert "Missing required environment variables" in str(exc_info.value)

def test_config_manual():
    """Test creating configuration manually."""
    config = M4300Config(
        host="switch.example.com",
        username="admin",
        password="password123"
    )
    
    assert config.host == "switch.example.com"
    assert config.username == "admin"
    assert config.password == "password123"
    assert config.port == 8443  # default value
    assert config.verify_ssl is True  # default value
    assert config.timeout == 30  # default value
    assert config.rate_limit == 10  # default value
    assert config.token_refresh_margin == 300  # default value

def test_config_base_url():
    """Test base URL generation."""
    config = M4300Config(
        host="switch.example.com",
        username="admin",
        password="password123",
        port=8444
    )
    
    assert config.base_url == "https://switch.example.com:8444/api/v1"

def test_config_invalid_port():
    """Test configuration with invalid port number."""
    with patch.dict(os.environ, {
        "M4300_HOST": "switch.example.com",
        "M4300_USERNAME": "admin",
        "M4300_PASSWORD": "password123",
        "M4300_PORT": "invalid"
    }):
        with pytest.raises(ValueError):
            M4300Config.from_env()

def test_config_invalid_verify_ssl():
    """Test configuration with invalid verify_ssl value."""
    with patch.dict(os.environ, {
        "M4300_HOST": "switch.example.com",
        "M4300_USERNAME": "admin",
        "M4300_PASSWORD": "password123",
        "M4300_VERIFY_SSL": "invalid"
    }):
        config = M4300Config.from_env()
        assert config.verify_ssl is False  # Invalid value defaults to False

def test_config_partial_env_vars(mock_env_vars):
    """Test configuration with partial environment variables."""
    partial_vars = mock_env_vars.copy()
    del partial_vars["M4300_VERIFY_SSL"]
    del partial_vars["M4300_TIMEOUT"]
    
    with patch.dict(os.environ, partial_vars, clear=True):
        config = M4300Config.from_env()
        
        assert config.verify_ssl is True  # default value
        assert config.timeout == 30  # default value

def test_config_repr():
    """Test string representation of config object."""
    config = M4300Config(
        host="switch.example.com",
        username="admin",
        password="password123"
    )
    
    repr_str = repr(config)
    assert "password123" not in repr_str  # Password should not be in string representation
    assert "switch.example.com" in repr_str
    assert "admin" in repr_str
