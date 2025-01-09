"""Unit tests for logout endpoint helper.

This module contains unit tests for the logout helper functionality.
These tests use mocked responses to verify behavior without requiring
access to a live switch.

Test Categories:
    1. Successful logout response handling
    2. Input parameter validation
    3. Error response handling
    4. Network error handling
    5. Response format validation
"""
import json
import pytest
import requests
from requests.exceptions import RequestException
from src.logout.logout import logout

def test_successful_logout(mocker):
    """Test successful logout with mocked response.
    
    Verifies:
        - Request format
        - Header validation
        - Response parsing
        - Return value structure
    """
    mock_response = {
        "logout": {},
        "resp": {
            "status": "success",
            "respCode": 0,
            "respMsg": "Operation success"
        }
    }
    
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.raise_for_status.return_value = None
    
    result = logout(
        "https://192.168.99.92:8443",
        "a11cd17543520ace80d7c7b45aba43357b4d0844995879364aa4d47b2671fe2e"
    )
    
    assert result == mock_response
    mock_post.assert_called_once_with(
        "https://192.168.99.92:8443/api/v1/logout",
        headers={
            "Accept": "application/json",
            "Authorization": "Bearer a11cd17543520ace80d7c7b45aba43357b4d0844995879364aa4d47b2671fe2e"
        },
        verify=False
    )

def test_missing_base_url():
    """Test error handling for missing base URL.
    
    Verifies:
        - Input validation
        - Error message format
        - ValueError exception
    """
    with pytest.raises(ValueError, match="base_url is required"):
        logout("", "valid_token")

def test_missing_token():
    """Test error handling for missing token.
    
    Verifies:
        - Input validation
        - Error message format
        - ValueError exception
    """
    with pytest.raises(ValueError, match="token is required"):
        logout("https://192.168.99.92:8443", "")

def test_failed_logout(mocker):
    """Test handling of failed logout attempt.
    
    Verifies:
        - Error response parsing
        - Error message format
        - RuntimeError exception
    """
    mock_response = {
        "logout": {},
        "resp": {
            "status": "failure",
            "respCode": 1,
            "respMsg": "Invalid token"
        }
    }
    
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Invalid token"):
        logout("https://192.168.99.92:8443", "invalid_token")

def test_invalid_response_format(mocker):
    """Test handling of invalid response format.
    
    Verifies:
        - Response validation
        - Error message format
        - RuntimeError exception
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = {"resp": {}}  # Missing logout object
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Invalid response format"):
        logout("https://192.168.99.92:8443", "valid_token")

def test_request_exception(mocker):
    """Test handling of request exception.
    
    Verifies:
        - Network error handling
        - Error message format
        - RuntimeError exception
    """
    mock_post = mocker.patch('requests.post')
    mock_post.side_effect = RequestException("Connection error")
    
    with pytest.raises(RuntimeError, match="API request failed: Connection error"):
        logout("https://192.168.99.92:8443", "valid_token")

def test_invalid_json_response(mocker):
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
    
    with pytest.raises(RuntimeError, match="Logout failed: Invalid JSON response"):
        logout("https://192.168.99.92:8443", "valid_token")
