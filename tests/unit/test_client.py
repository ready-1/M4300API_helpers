"""Tests for API client."""

import time
from unittest.mock import Mock, patch

import pytest
import requests
import responses

from m4300api_helpers.client import M4300Client
from m4300api_helpers.config import M4300Config
from m4300api_helpers.exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    InvalidCredentialsError,
    RateLimitError,
    TimeoutError,
    TokenExpiredError,
)
from tests.fixtures.api_responses import (
    DEVICE_INFO_SUCCESS,
    LOGIN_FAILURE,
    LOGIN_SUCCESS,
    RATE_LIMIT_EXCEEDED,
    TOKEN_EXPIRED,
    VLAN_CONFIG_SUCCESS,
)

@pytest.fixture
def config():
    """Create test configuration."""
    return M4300Config(
        host="switch.example.com",
        username="admin",
        password="password123"
    )

@pytest.fixture
def client(config):
    """Create test client."""
    return M4300Client(config)

@responses.activate
def test_authentication_success(client):
    """Test successful authentication."""
    responses.add(
        responses.POST,
        f"{client.config.base_url}/login",
        json=LOGIN_SUCCESS,
        status=200
    )
    
    client.authenticate()
    
    assert client._auth_token == "example-token-12345"
    assert client._token_expires is not None

@responses.activate
def test_authentication_failure(client):
    """Test authentication failure."""
    responses.add(
        responses.POST,
        f"{client.config.base_url}/login",
        json=LOGIN_FAILURE,
        status=401
    )
    
    with pytest.raises(InvalidCredentialsError):
        client.authenticate()

def test_token_expiry_check(client):
    """Test token expiry checking."""
    client._auth_token = "test-token"
    client._token_expires = time.time() - 100  # Token expired 100 seconds ago
    
    with pytest.raises(TokenExpiredError):
        client._check_token_expiry()

@responses.activate
def test_rate_limiting(client):
    """Test rate limiting."""
    # Configure client with strict rate limit
    client.config.rate_limit = 2  # 2 requests per second
    
    # Add mock responses
    responses.add(
        responses.POST,
        f"{client.config.base_url}/login",
        json=LOGIN_SUCCESS,
        status=200
    )
    responses.add(
        responses.GET,
        f"{client.config.base_url}/device_info",
        json=DEVICE_INFO_SUCCESS,
        status=200
    )
    
    # Make requests and measure time
    start_time = time.time()
    client.authenticate()
    client.get("device_info")
    elapsed = time.time() - start_time
    
    # Should take at least 0.5 seconds due to rate limiting
    assert elapsed >= 0.5

@responses.activate
def test_rate_limit_exceeded(client):
    """Test rate limit exceeded error."""
    responses.add(
        responses.POST,
        f"{client.config.base_url}/login",
        json=LOGIN_SUCCESS,
        status=200
    )
    responses.add(
        responses.GET,
        f"{client.config.base_url}/device_info",
        json=RATE_LIMIT_EXCEEDED,
        status=429
    )
    
    client.authenticate()
    with pytest.raises(RateLimitError):
        client.get("device_info")

@responses.activate
def test_token_refresh_on_expiry(client):
    """Test automatic token refresh when expired."""
    # First login
    responses.add(
        responses.POST,
        f"{client.config.base_url}/login",
        json=LOGIN_SUCCESS,
        status=200
    )
    
    # First request fails with token expired
    responses.add(
        responses.GET,
        f"{client.config.base_url}/device_info",
        json=TOKEN_EXPIRED,
        status=401
    )
    
    # Second login for refresh
    responses.add(
        responses.POST,
        f"{client.config.base_url}/login",
        json=LOGIN_SUCCESS,
        status=200
    )
    
    # Final successful request
    responses.add(
        responses.GET,
        f"{client.config.base_url}/device_info",
        json=DEVICE_INFO_SUCCESS,
        status=200
    )
    
    response = client.get("device_info")
    assert response == DEVICE_INFO_SUCCESS

def test_connection_error(client):
    """Test connection error handling."""
    with patch.object(requests.Session, 'request') as mock_request:
        mock_request.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(ConnectionError):
            client.get("device_info")

def test_timeout_error(client):
    """Test timeout error handling."""
    with patch.object(requests.Session, 'request') as mock_request:
        mock_request.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(TimeoutError):
            client.get("device_info")

@responses.activate
def test_successful_get_request(client):
    """Test successful GET request."""
    responses.add(
        responses.POST,
        f"{client.config.base_url}/login",
        json=LOGIN_SUCCESS,
        status=200
    )
    responses.add(
        responses.GET,
        f"{client.config.base_url}/device_info",
        json=DEVICE_INFO_SUCCESS,
        status=200
    )
    
    response = client.get("device_info")
    assert response == DEVICE_INFO_SUCCESS

@responses.activate
def test_successful_post_request(client):
    """Test successful POST request."""
    responses.add(
        responses.POST,
        f"{client.config.base_url}/login",
        json=LOGIN_SUCCESS,
        status=200
    )
    responses.add(
        responses.POST,
        f"{client.config.base_url}/swcfg_vlan",
        json=VLAN_CONFIG_SUCCESS,
        status=200
    )
    
    response = client.post("swcfg_vlan", json={
        "switchConfigVlan": {
            "vlanId": 100,
            "name": "Engineering"
        }
    })
    assert response == VLAN_CONFIG_SUCCESS

@responses.activate
def test_request_with_params(client):
    """Test request with query parameters."""
    responses.add(
        responses.POST,
        f"{client.config.base_url}/login",
        json=LOGIN_SUCCESS,
        status=200
    )
    responses.add(
        responses.GET,
        f"{client.config.base_url}/swcfg_vlan",
        json=VLAN_CONFIG_SUCCESS,
        status=200
    )
    
    response = client.get("swcfg_vlan", params={"vlanid": 100})
    assert response == VLAN_CONFIG_SUCCESS
    assert responses.calls[-1].request.url.endswith("vlanid=100")

def test_session_configuration(client):
    """Test session configuration."""
    session = client._create_session()
    
    assert session.verify == client.config.verify_ssl
    assert isinstance(session.adapters["https://"], requests.adapters.HTTPAdapter)
    
    # Test retry configuration
    adapter = session.adapters["https://"]
    assert adapter.max_retries.total == 3
    assert adapter.max_retries.backoff_factor == 0.5
    assert set(adapter.max_retries.status_forcelist) == {500, 502, 503, 504}
