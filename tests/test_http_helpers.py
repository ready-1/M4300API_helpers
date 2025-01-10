"""Tests for HTTP helper functions."""

import os
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import Timeout

from m4300api_helpers.http_helpers import (
    build_switch_url,
    make_api_call,
    AuthError,
    M4300Error,
)


@pytest.fixture
def mock_session(mocker):
    """Create a mock requests.Session."""
    mock = mocker.patch("requests.Session", autospec=True)
    return mock.return_value


@pytest.fixture
def auth_callback():
    """Create a mock auth callback."""
    return Mock(return_value=("admin", "password"))


def test_build_switch_url_basic() -> None:
    """Test basic URL construction."""
    url = build_switch_url("192.168.1.1", "/device_info")
    assert url == "https://192.168.1.1:8443/api/v1/device_info"


def test_build_switch_url_custom_port() -> None:
    """Test URL construction with custom port."""
    url = build_switch_url("switch.local", "/login", port=443)
    assert url == "https://switch.local:443/api/v1/login"


def test_build_switch_url_strip_protocol() -> None:
    """Test stripping of existing protocol."""
    url = build_switch_url("https://192.168.1.1", "/status")
    assert url == "https://192.168.1.1:8443/api/v1/status"


def test_build_switch_url_normalize_slashes() -> None:
    """Test path normalization with slashes."""
    cases = [
        ("/status/", "https://192.168.1.1:8443/api/v1/status"),
        ("status", "https://192.168.1.1:8443/api/v1/status"),
        ("//status//", "https://192.168.1.1:8443/api/v1/status"),
    ]
    for endpoint, expected in cases:
        url = build_switch_url("192.168.1.1", endpoint)
        assert url == expected


def test_build_switch_url_query_params() -> None:
    """Test URL construction with query parameters."""
    url = build_switch_url("192.168.1.1", "/config?type=network")
    assert url == "https://192.168.1.1:8443/api/v1/config?type=network"


def test_build_switch_url_empty_hostname() -> None:
    """Test error handling for empty hostname."""
    with pytest.raises(ValueError, match="Hostname cannot be empty"):
        build_switch_url("", "/status")


def test_build_switch_url_invalid_hostname() -> None:
    """Test error handling for invalid hostname format."""
    with pytest.raises(ValueError, match="Invalid hostname format"):
        build_switch_url("switch@domain", "/status")


def test_build_switch_url_empty_endpoint() -> None:
    """Test error handling for empty endpoint."""
    with pytest.raises(ValueError, match="Endpoint cannot be empty"):
        build_switch_url("192.168.1.1", "")


def test_build_switch_url_invalid_endpoint() -> None:
    """Test error handling for invalid endpoint format."""
    with pytest.raises(ValueError, match="Invalid endpoint format"):
        build_switch_url("192.168.1.1", "/config<script>")


def test_build_switch_url_invalid_port() -> None:
    """Test error handling for invalid port range."""
    cases = [-1, 0, 65536, 70000]
    for port in cases:
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            build_switch_url("192.168.1.1", "/status", port=port)


@pytest.mark.integration
def test_build_switch_url_integration() -> None:
    """Integration test with example endpoints."""
    endpoints = [
        "/login",
        "/device_info",
        "/config?type=system",
        "/firmware/status",
    ]
    for endpoint in endpoints:
        url = build_switch_url("192.168.1.1", endpoint)
        assert url.startswith("https://")
        assert "/api/v1/" in url
        assert url.endswith(endpoint.lstrip("/"))


def test_make_api_call_success(mock_session):
    """Test successful API call."""
    mock_response = Mock(ok=True)
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"status": "success"}
    mock_session.request.return_value = mock_response

    response, token = make_api_call(
        method="GET",
        url="https://192.168.1.1:8443/api/v1/device_info",
        token="valid_token",
        auth_callback=lambda: ("admin", "password"),
    )

    assert response == {"status": "success"}
    assert token is None
    mock_session.request.assert_called_once()


@patch("m4300api_helpers.http_helpers.login")
def test_make_api_call_token_refresh(mock_login, mock_session, auth_callback):
    """Test token refresh flow."""
    # First call returns 401
    mock_401 = Mock(ok=False, status_code=401)
    mock_401.raise_for_status = Mock()  # Don't raise error, let code handle 401
    mock_401.json.return_value = {"error": "Unauthorized"}

    # Login helper returns new token
    mock_login.return_value = {
        "data": {"token": "new_token", "expire": "86400"},
        "resp": {"status": "success", "respCode": 0, "respMsg": "Success"},
    }

    # Final call succeeds
    mock_success = Mock(ok=True, status_code=200)
    mock_success.raise_for_status = Mock()
    mock_success.json.return_value = {"status": "success"}

    def request_side_effect(method, url, **kwargs):
        # Request with new token
        if kwargs.get("headers", {}).get("Authorization") == "Bearer new_token":
            return mock_success
        # First request with old token
        return mock_401

    mock_session.request.side_effect = request_side_effect

    response, token = make_api_call(
        method="GET",
        url="https://192.168.1.1:8443/api/v1/device_info",
        token="old_token",
        auth_callback=auth_callback,
    )

    # Verify final response and new token
    assert response == {"status": "success"}
    assert token == "new_token"

    # Verify all requests were made
    assert (
        mock_session.request.call_count == 2
    )  # Initial request + retry with new token

    # Verify auth callback was called
    auth_callback.assert_called_once()

    # Verify login helper was called
    mock_login.assert_called_once_with("https://192.168.1.1:8443", "admin", "password")


def test_make_api_call_retry_timeout(mock_session):
    """Test retry on timeout."""
    mock_session.request.side_effect = [
        Timeout(),
        Timeout(),
        Mock(
            ok=True,
            raise_for_status=Mock(),
            json=Mock(return_value={"status": "success"}),
        ),
    ]

    response, token = make_api_call(
        method="GET",
        url="https://192.168.1.1:8443/api/v1/device_info",
        token="valid_token",
        auth_callback=lambda: ("admin", "password"),
    )

    assert response == {"status": "success"}
    assert token is None
    assert mock_session.request.call_count == 3


def test_make_api_call_max_retries(mock_session):
    """Test max retries exceeded."""
    mock_session.request.side_effect = Timeout()

    with pytest.raises(M4300Error, match="Request failed after 3 attempts"):
        make_api_call(
            method="GET",
            url="https://192.168.1.1:8443/api/v1/device_info",
            token="valid_token",
            auth_callback=lambda: ("admin", "password"),
        )

    assert mock_session.request.call_count == 3


@patch("m4300api_helpers.http_helpers.login")
def test_make_api_call_auth_error(mock_login, mock_session, auth_callback):
    """Test authentication error handling."""
    # First call returns 401
    mock_401 = Mock(ok=False, status_code=401)
    mock_401.raise_for_status = Mock()  # Don't raise error, let code handle 401
    mock_401.json.return_value = {"error": "Unauthorized"}

    # Login helper fails
    mock_login.side_effect = RuntimeError("Invalid credentials")

    mock_session.request.return_value = mock_401

    with pytest.raises(AuthError, match="Failed to refresh authentication token"):
        make_api_call(
            method="GET",
            url="https://192.168.1.1:8443/api/v1/device_info",
            token="old_token",
            auth_callback=auth_callback,
        )

    # Verify auth callback was called
    auth_callback.assert_called_once()

    # Verify login helper was called
    mock_login.assert_called_once_with("https://192.168.1.1:8443", "admin", "password")


def test_make_api_call_ssl_verify(mock_session):
    """Test SSL verification configuration."""
    mock_response = Mock(ok=True)
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"status": "success"}
    mock_session.request.return_value = mock_response

    # Test with environment variable
    os.environ["M4300_SSL_VERIFY"] = "false"
    make_api_call(
        method="GET",
        url="https://192.168.1.1:8443/api/v1/device_info",
        token="valid_token",
        auth_callback=lambda: ("admin", "password"),
    )
    mock_session.request.assert_called_with(
        method="GET",
        url="https://192.168.1.1:8443/api/v1/device_info",
        headers={"Authorization": "Bearer valid_token"},
        data=None,
        params=None,
        files=None,
        cookies=None,
        verify=False,
        timeout=30,
        allow_redirects=True,
        stream=False,
    )


@pytest.mark.integration
def test_make_api_call_integration(mock_session):
    """Integration test with various request configurations."""
    mock_response = Mock(ok=True)
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"status": "success"}
    mock_session.request.return_value = mock_response

    test_cases = [
        {
            "method": "GET",
            "data": None,
            "params": {"filter": "active"},
        },
        {
            "method": "POST",
            "data": {"name": "test"},
            "files": {"file": "content"},
        },
        {
            "method": "PUT",
            "data": {"status": "updated"},
            "headers": {"Custom": "value"},
        },
    ]

    for case in test_cases:
        response, _ = make_api_call(
            url="https://192.168.1.1:8443/api/v1/device_info",
            token="valid_token",
            auth_callback=lambda: ("admin", "password"),
            **case,
        )
        assert response == {"status": "success"}
