"""Tests for login endpoint helper."""
import json
import pytest
import requests
from requests.exceptions import RequestException
from src.login.login import login

def test_successful_login(mocker):
    """Test successful login with valid credentials."""
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
    
    result = login("https://192.168.99.92:8443", "admin", "password123")
    
    assert result == mock_response
    mock_post.assert_called_once_with(
        "https://192.168.99.92:8443/api/v1/login",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        data=json.dumps({
            "login": {
                "username": "admin",
                "password": "password123"
            }
        })
    )

def test_missing_base_url():
    """Test error handling for missing base URL."""
    with pytest.raises(ValueError, match="base_url is required"):
        login("", "admin", "password123")

def test_missing_username():
    """Test error handling for missing username."""
    with pytest.raises(ValueError, match="username is required"):
        login("https://192.168.99.92:8443", "", "password123")

def test_missing_password():
    """Test error handling for missing password."""
    with pytest.raises(ValueError, match="password is required"):
        login("https://192.168.99.92:8443", "admin", "")

def test_failed_login(mocker):
    """Test handling of failed login attempt."""
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
        login("https://192.168.99.92:8443", "admin", "wrong_password")

def test_invalid_response_format(mocker):
    """Test handling of invalid response format."""
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = {"login": {}, "resp": {}}
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Invalid response format"):
        login("https://192.168.99.92:8443", "admin", "password123")

def test_request_exception(mocker):
    """Test handling of request exception."""
    mock_post = mocker.patch('requests.post')
    mock_post.side_effect = RequestException("Connection error")
    
    with pytest.raises(RuntimeError, match="API request failed: Connection error"):
        login("https://192.168.99.92:8443", "admin", "password123")

def test_invalid_json_response(mocker):
    """Test handling of invalid JSON response."""
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Invalid JSON response"):
        login("https://192.168.99.92:8443", "admin", "password123")
