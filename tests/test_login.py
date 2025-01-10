"""Unit tests for login helper module."""

import json
import pytest
from requests.exceptions import RequestException
from m4300api_helpers.login import login


def test_successful_login(mocker, switch_config):
    """Test successful login with mocked response.

    Verifies:
        - Request format
        - Header validation
        - Response parsing
        - Return value structure
    """
    mock_response = {
        "login": {
            "token": "8c523ad44e0a8f46324aa71f371963e07211b04b7239519a6f60f1ee5939dcc0b1db6b49394ff6866a67c45a396993f9a21359c3abe595821f579cfd25fafeeb",
            "expire": "86400",
        },
        "resp": {"status": "success", "respCode": 0, "respMsg": "Operation success"},
    }

    mock_post = mocker.patch("requests.post")
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.raise_for_status.return_value = None

    result = login(
        switch_config["base_url"], switch_config["username"], switch_config["password"]
    )

    expected = {
        "data": {
            "token": mock_response["login"]["token"],
            "expire": mock_response["login"]["expire"],
        },
        "resp": mock_response["resp"],
    }
    assert result == expected

    mock_post.assert_called_once_with(
        f"{switch_config['base_url']}/api/v1/login",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        data=json.dumps(
            {
                "login": {
                    "username": switch_config["username"],
                    "password": switch_config["password"],
                }
            }
        ),
        verify=False,
        timeout=10,
    )


def test_missing_base_url(switch_config):
    """Test login with missing base_url.

    Verifies:
        - Parameter validation
        - Error message
    """
    with pytest.raises(ValueError, match="base_url is required"):
        login("", switch_config["username"], switch_config["password"])


def test_missing_username(switch_config):
    """Test login with missing username.

    Verifies:
        - Parameter validation
        - Error message
    """
    with pytest.raises(ValueError, match="username is required"):
        login(switch_config["base_url"], "", switch_config["password"])


def test_missing_password(switch_config):
    """Test login with missing password.

    Verifies:
        - Parameter validation
        - Error message
    """
    with pytest.raises(ValueError, match="password is required"):
        login(switch_config["base_url"], switch_config["username"], "")


def test_invalid_response_format(mocker, switch_config):
    """Test login with invalid response format.

    Verifies:
        - Response validation
        - Error message
    """
    mock_response = {"invalid": "format"}

    mock_post = mocker.patch("requests.post")
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.raise_for_status.return_value = None

    with pytest.raises(RuntimeError, match="Invalid response format"):
        login(
            switch_config["base_url"],
            switch_config["username"],
            switch_config["password"],
        )


def test_error_response(mocker, switch_config):
    """Test login with error response.

    Verifies:
        - Error response handling
        - Error message format
    """
    mock_response = {
        "login": {},
        "resp": {"status": "failure", "respCode": 1, "respMsg": "Test error message"},
    }

    mock_post = mocker.patch("requests.post")
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.raise_for_status.return_value = None

    with pytest.raises(RuntimeError, match="Login failed: Test error message"):
        login(
            switch_config["base_url"],
            switch_config["username"],
            switch_config["password"],
        )


def test_invalid_json_response(mocker, switch_config):
    """Test login with invalid JSON response.

    Verifies:
        - JSON parsing error handling
        - Error message
    """
    mock_post = mocker.patch("requests.post")
    mock_post.return_value.json.side_effect = json.JSONDecodeError("Test error", "", 0)
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.text = "Invalid JSON"

    with pytest.raises(RuntimeError, match="Login failed: Invalid JSON response"):
        login(
            switch_config["base_url"],
            switch_config["username"],
            switch_config["password"],
        )


def test_request_exception(mocker, switch_config):
    """Test login with request exception.

    Verifies:
        - Network error handling
        - Error message format
    """
    mock_post = mocker.patch("requests.post")
    mock_post.side_effect = RequestException("Test error")

    with pytest.raises(RuntimeError, match="API request failed: Test error"):
        login(
            switch_config["base_url"],
            switch_config["username"],
            switch_config["password"],
        )
