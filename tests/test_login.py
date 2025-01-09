"""Unit tests for login endpoint helper.

This module contains unit tests for the login helper functionality.
These tests use mocked responses to verify behavior without requiring
access to a live switch.

Test Categories:
    1. Successful login response handling
    2. Input parameter validation
    3. Error response handling
    4. Network error handling
    5. Response format validation
"""
import json
import pytest
import requests
from requests.exceptions import RequestException
from m4300api_helpers.login.login import login, DEFAULT_TIMEOUT

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
            "expire": "86400"
        },
        "resp": {
            "status": "success",
            "respCode": 0,
            "respMsg": "Operation success"
        }
    }
    
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.raise_for_status.return_value = None
    
    result = login(switch_config["base_url"], switch_config["username"], switch_config["password"])
    
    assert result == mock_response
    mock_post.assert_called_once_with(
        f"{switch_config['base_url']}/api/v1/login",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        data=json.dumps({
            "login": {
                "username": switch_config["username"],
                "password": switch_config["password"]
            }
        }),
        verify=False,
        timeout=DEFAULT_TIMEOUT
    )

def test_missing_base_url(switch_config):
    """Test error handling for missing base URL.
    
    Verifies:
        - Input validation
        - Error message format
        - ValueError exception
    """
    with pytest.raises(ValueError, match="base_url is required"):
        login("", switch_config["username"], switch_config["password"])

def test_missing_username(switch_config):
    """Test error handling for missing username.
    
    Verifies:
        - Input validation
        - Error message format
        - ValueError exception
    """
    with pytest.raises(ValueError, match="username is required"):
        login(switch_config["base_url"], "", switch_config["password"])

def test_missing_password(switch_config):
    """Test error handling for missing password.
    
    Verifies:
        - Input validation
        - Error message format
        - ValueError exception
    """
    with pytest.raises(ValueError, match="password is required"):
        login(switch_config["base_url"], switch_config["username"], "")

def test_failed_login(mocker, switch_config):
    """Test handling of failed login attempt.
    
    Verifies:
        - Error response parsing
        - Error message format
        - RuntimeError exception
    """
    mock_response = {
        "login": {
            "token": "",
            "expire": "0"
        },
        "resp": {
            "status": "failure",
            "respCode": 1,
            "respMsg": "Invalid credentials"
        }
    }
    
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Login failed: Invalid credentials"):
        login(switch_config["base_url"], switch_config["username"], "wrong_password")

def test_invalid_response_format(mocker, switch_config):
    """Test handling of invalid response format.
    
    Verifies:
        - Response validation
        - Error message format
        - RuntimeError exception
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = {"resp": {}}  # Missing login object
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Invalid response format"):
        login(switch_config["base_url"], switch_config["username"], switch_config["password"])

def test_request_exception(mocker, switch_config):
    """Test handling of request exception.
    
    Verifies:
        - Network error handling
        - Error message format
        - RuntimeError exception
    """
    mock_post = mocker.patch('requests.post')
    mock_post.side_effect = RequestException("Connection error")
    
    with pytest.raises(RuntimeError, match="API request failed: Connection error"):
        login(switch_config["base_url"], switch_config["username"], switch_config["password"])

def test_invalid_json_response(mocker, switch_config):
    """Test handling of invalid JSON response.
    
    Verifies:
        - JSON parsing error handling
        - Error message format
        - RuntimeError exception
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_post.return_value.text = "Invalid JSON response"
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Login failed: Invalid JSON response"):
        login(switch_config["base_url"], switch_config["username"], switch_config["password"])
