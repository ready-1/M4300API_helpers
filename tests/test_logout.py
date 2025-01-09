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
from m4300api_helpers.logout.logout import logout, DEFAULT_TIMEOUT

@pytest.fixture
def test_token():
    """Fixture providing a test token for logout tests."""
    return "8c523ad44e0a8f46324aa71f371963e07211b04b7239519a6f60f1ee5939dcc0"

def test_successful_logout(mocker, switch_config, test_token):
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
    
    result = logout(switch_config["base_url"], test_token)
    
    assert result == mock_response
    mock_post.assert_called_once_with(
        f"{switch_config['base_url']}/api/v1/logout",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {test_token}"
        },
        verify=False,
        timeout=DEFAULT_TIMEOUT
    )

def test_missing_base_url(test_token):
    """Test error handling for missing base URL.
    
    Verifies:
        - Input validation
        - Error message format
        - ValueError exception
    """
    with pytest.raises(ValueError, match="base_url is required"):
        logout("", test_token)

def test_missing_token(switch_config):
    """Test error handling for missing token.
    
    Verifies:
        - Input validation
        - Error message format
        - ValueError exception
    """
    with pytest.raises(ValueError, match="token is required"):
        logout(switch_config["base_url"], "")

def test_failed_logout(mocker, switch_config, test_token):
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
        logout(switch_config["base_url"], "invalid_token")

def test_invalid_response_type(mocker, switch_config, test_token):
    """Test handling of non-dict response.
    
    Verifies:
        - Response type validation
        - Error message format
        - RuntimeError exception
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = ["not", "a", "dict"]  # Invalid type
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Invalid response type"):
        logout(switch_config["base_url"], test_token)

def test_missing_resp_field(mocker, switch_config, test_token):
    """Test handling of missing resp field.
    
    Verifies:
        - Response structure validation
        - Error message format
        - RuntimeError exception
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = {"logout": {}}  # Missing resp field
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Missing response data"):
        logout(switch_config["base_url"], test_token)

def test_invalid_response_format(mocker, switch_config, test_token):
    """Test handling of invalid response format.
    
    Verifies:
        - Response validation
        - Error message format
        - RuntimeError exception
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = {"resp": {}}  # Missing logout object
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Missing status"):
        logout(switch_config["base_url"], test_token)

def test_request_exception(mocker, switch_config, test_token):
    """Test handling of request exception.
    
    Verifies:
        - Network error handling
        - Error message format
        - RuntimeError exception
    """
    mock_post = mocker.patch('requests.post')
    mock_post.side_effect = RequestException("Connection error")
    
    with pytest.raises(RuntimeError, match="Logout failed: Connection error"):
        logout(switch_config["base_url"], test_token)

def test_type_error_response(mocker, switch_config, test_token):
    """Test handling of TypeError in response processing.
    
    Verifies:
        - Type error handling
        - Error message format
        - RuntimeError exception
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = {"resp": None}  # Will cause TypeError on dict access
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Invalid response format"):
        logout(switch_config["base_url"], test_token)

def test_invalid_json_response(mocker, switch_config, test_token):
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
        logout(switch_config["base_url"], test_token)
