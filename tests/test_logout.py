"""Unit tests for logout helper module."""

import json
import pytest
from requests.exceptions import RequestException
from m4300api_helpers.logout import logout


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
    
    expected = {
        "data": {},
        "resp": mock_response["resp"]
    }
    assert result == expected
    
    mock_post.assert_called_once_with(
        f"{switch_config['base_url']}/api/v1/logout",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {test_token}"
        },
        verify=False,
        timeout=10
    )


def test_missing_base_url(test_token):
    """Test logout with missing base_url.
    
    Verifies:
        - Parameter validation
        - Error message
    """
    with pytest.raises(ValueError, match="base_url is required"):
        logout("", test_token)


def test_missing_token(switch_config):
    """Test logout with missing token.
    
    Verifies:
        - Parameter validation
        - Error message
    """
    with pytest.raises(ValueError, match="token is required"):
        logout(switch_config["base_url"], "")


def test_invalid_response_type(mocker, switch_config, test_token):
    """Test logout with invalid response type.
    
    Verifies:
        - Response validation
        - Error message
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = "invalid"
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Invalid response type"):
        logout(switch_config["base_url"], test_token)


def test_missing_response_data(mocker, switch_config, test_token):
    """Test logout with missing response data.
    
    Verifies:
        - Response validation
        - Error message
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = {}
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Missing response data"):
        logout(switch_config["base_url"], test_token)


def test_invalid_response_format(mocker, switch_config, test_token):
    """Test logout with invalid response format.
    
    Verifies:
        - Response validation
        - Error message
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = {"resp": None}
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Invalid response format"):
        logout(switch_config["base_url"], test_token)


def test_missing_status(mocker, switch_config, test_token):
    """Test logout with missing status.
    
    Verifies:
        - Response validation
        - Error message
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = {"resp": {}}
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Missing status"):
        logout(switch_config["base_url"], test_token)


def test_error_response(mocker, switch_config, test_token):
    """Test logout with error response.
    
    Verifies:
        - Error response handling
        - Error message format
    """
    mock_response = {
        "logout": {},
        "resp": {
            "status": "failure",
            "respCode": 1,
            "respMsg": "Test error message"
        }
    }
    
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Test error message"):
        logout(switch_config["base_url"], test_token)


def test_invalid_json_response(mocker, switch_config, test_token):
    """Test logout with invalid JSON response.
    
    Verifies:
        - JSON parsing error handling
        - Error message
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.side_effect = json.JSONDecodeError("Test error", "", 0)
    mock_post.return_value.raise_for_status.return_value = None
    
    with pytest.raises(RuntimeError, match="Logout failed: Invalid JSON response"):
        logout(switch_config["base_url"], test_token)


def test_request_exception(mocker, switch_config, test_token):
    """Test logout with request exception.
    
    Verifies:
        - Network error handling
        - Error message format
    """
    mock_post = mocker.patch('requests.post')
    mock_post.side_effect = RequestException("Test error")
    
    with pytest.raises(RuntimeError, match="Logout failed: Connection error"):
        logout(switch_config["base_url"], test_token)
