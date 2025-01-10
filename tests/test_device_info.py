"""Unit tests for device info helper module."""

import json
import pytest
from m4300api_helpers.device_info import get_device_info


def test_successful_device_info(
    mocker, switch_config, test_token, mock_success_response
):
    """Test successful device info retrieval with mocked response.

    Verifies:
        - Request format
        - Header validation
        - Response parsing
        - Return value structure
        - Type casting
    """
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = mock_success_response
    mock_get.return_value.raise_for_status.return_value = None

    result = get_device_info(switch_config["base_url"], test_token)

    expected = {
        "data": mock_success_response["deviceInfo"],
        "resp": mock_success_response["resp"],
    }
    assert result == expected

    mock_get.assert_called_once_with(
        f"{switch_config['base_url']}/api/v1/device_info",
        headers={"Accept": "application/json", "Authorization": f"Bearer {test_token}"},
        verify=False,
        timeout=10,
    )


def test_missing_base_url(test_token):
    """Test device info with missing base_url.

    Verifies:
        - Parameter validation
        - Error message
    """
    with pytest.raises(ValueError, match="base_url is required"):
        get_device_info("", test_token)


def test_missing_token(switch_config):
    """Test device info with missing token.

    Verifies:
        - Parameter validation
        - Error message
    """
    with pytest.raises(ValueError, match="token is required"):
        get_device_info(switch_config["base_url"], "")


def test_invalid_response_type(mocker, switch_config, test_token):
    """Test device info with invalid response type.

    Verifies:
        - Response validation
        - Error message
    """
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = "invalid"
    mock_get.return_value.raise_for_status.return_value = None

    with pytest.raises(RuntimeError, match="Device info failed: Invalid response type"):
        get_device_info(switch_config["base_url"], test_token)


def test_missing_response_data(mocker, switch_config, test_token):
    """Test device info with missing response data.

    Verifies:
        - Response validation
        - Error message
    """
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {}
    mock_get.return_value.raise_for_status.return_value = None

    with pytest.raises(RuntimeError, match="Device info failed: Missing response data"):
        get_device_info(switch_config["base_url"], test_token)


def test_invalid_response_format(mocker, switch_config, test_token):
    """Test device info with invalid response format.

    Verifies:
        - Response validation
        - Error message
    """
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"resp": None}
    mock_get.return_value.raise_for_status.return_value = None

    with pytest.raises(
        RuntimeError, match="Device info failed: Invalid response format"
    ):
        get_device_info(switch_config["base_url"], test_token)


def test_missing_status(mocker, switch_config, test_token):
    """Test device info with missing status.

    Verifies:
        - Response validation
        - Error message
    """
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"resp": {}}
    mock_get.return_value.raise_for_status.return_value = None

    with pytest.raises(RuntimeError, match="Device info failed: Missing status"):
        get_device_info(switch_config["base_url"], test_token)


def test_error_response(mocker, switch_config, test_token):
    """Test device info with error response.

    Verifies:
        - Error response handling
        - Error message format
    """
    mock_response = {
        "deviceInfo": {},
        "resp": {"status": "failure", "respCode": 1, "respMsg": "Test error message"},
    }

    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.raise_for_status.return_value = None

    with pytest.raises(RuntimeError, match="Device info failed: Test error message"):
        get_device_info(switch_config["base_url"], test_token)


def test_invalid_json_response(mocker, switch_config, test_token):
    """Test device info with invalid JSON response.

    Verifies:
        - JSON parsing error handling
        - Error message
    """
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.side_effect = json.JSONDecodeError("Test error", "", 0)
    mock_get.return_value.raise_for_status.return_value = None

    with pytest.raises(RuntimeError, match="Device info failed: Invalid JSON response"):
        get_device_info(switch_config["base_url"], test_token)
