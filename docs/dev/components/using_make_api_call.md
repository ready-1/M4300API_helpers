# Using make_api_call in New Helpers

## Overview

This guide explains how to use the `make_api_call` helper when implementing new endpoint helpers. The `make_api_call` helper handles authentication, retries, and error handling, allowing you to focus on endpoint-specific logic.

## Basic Pattern

```python
from ..http_helpers import make_api_call, build_switch_url

def my_endpoint(base_url: str, token: str, auth_callback: Callable[[], tuple[str, str]]) -> ApiResult[MyResponse]:
    """Implement endpoint-specific logic here.

    Args:
        base_url: Base URL of the API (e.g., https://192.168.99.92:8443)
        token: Current authentication token
        auth_callback: Function that returns (username, password) for token refresh

    Returns:
        ApiResult containing endpoint-specific response data
    """
    # 1. Build the endpoint URL
    url = build_switch_url(
        hostname=urlparse(base_url).netloc.split(":")[0],
        endpoint="/my-endpoint"
    )

    # 2. Make the API call
    response, new_token = make_api_call(
        method="GET",  # or POST, PUT, etc.
        url=url,
        token=token,
        auth_callback=auth_callback
    )

    # 3. Return structured response
    return {
        "data": MyResponse(**response["my-endpoint"]),
        "resp": ResponseData(
            status=response["resp"]["status"],
            respCode=response["resp"]["respCode"],
            respMsg=response["resp"]["respMsg"]
        )
    }
```

## Common Use Cases

### 1. GET Request

```python
def get_device_info(base_url: str, token: str, auth_callback: Callable[[], tuple[str, str]]) -> ApiResult[DeviceInfo]:
    """Get device information."""
    url = build_switch_url(urlparse(base_url).netloc.split(":")[0], "/device_info")

    response, new_token = make_api_call(
        method="GET",
        url=url,
        token=token,
        auth_callback=auth_callback
    )

    return {
        "data": DeviceInfo(**response["device_info"]),
        "resp": ResponseData(**response["resp"])
    }
```

### 2. POST Request with Data

```python
def update_config(
    base_url: str,
    token: str,
    auth_callback: Callable[[], tuple[str, str]],
    config: Dict[str, Any]
) -> ApiResult[ConfigResponse]:
    """Update device configuration."""
    url = build_switch_url(urlparse(base_url).netloc.split(":")[0], "/config")

    response, new_token = make_api_call(
        method="POST",
        url=url,
        token=token,
        auth_callback=auth_callback,
        data={"config": config}  # Request payload
    )

    return {
        "data": ConfigResponse(**response["config"]),
        "resp": ResponseData(**response["resp"])
    }
```

### 3. File Upload

```python
def upload_firmware(
    base_url: str,
    token: str,
    auth_callback: Callable[[], tuple[str, str]],
    firmware_path: str
) -> ApiResult[UploadResponse]:
    """Upload firmware file."""
    url = build_switch_url(urlparse(base_url).netloc.split(":")[0], "/firmware/upload")

    with open(firmware_path, 'rb') as f:
        response, new_token = make_api_call(
            method="POST",
            url=url,
            token=token,
            auth_callback=auth_callback,
            files={'firmware': f},
            timeout=(5, 300)  # 5s connect, 5min read
        )

    return {
        "data": UploadResponse(**response["upload"]),
        "resp": ResponseData(**response["resp"])
    }
```

### 4. Query Parameters

```python
def get_logs(
    base_url: str,
    token: str,
    auth_callback: Callable[[], tuple[str, str]],
    start_time: str,
    end_time: str
) -> ApiResult[LogResponse]:
    """Get logs within time range."""
    url = build_switch_url(urlparse(base_url).netloc.split(":")[0], "/logs")

    response, new_token = make_api_call(
        method="GET",
        url=url,
        token=token,
        auth_callback=auth_callback,
        params={  # URL query parameters
            "start": start_time,
            "end": end_time
        }
    )

    return {
        "data": LogResponse(**response["logs"]),
        "resp": ResponseData(**response["resp"])
    }
```

## Error Handling

The `make_api_call` helper handles common errors:

1. Authentication failures (401)
   - Automatically refreshes token
   - Retries original request
   - Raises AuthError if refresh fails

2. Network issues
   - Retries on timeouts
   - Retries on connection errors
   - Raises M4300Error after max retries

3. Server errors (5xx)
   - Retries with exponential backoff
   - Raises original error after max retries

Your helper should handle endpoint-specific errors:

```python
def my_endpoint(base_url: str, token: str, auth_callback: Callable[[], tuple[str, str]]) -> ApiResult[MyResponse]:
    """Implement endpoint with error handling."""
    try:
        response, new_token = make_api_call(...)

        # Handle endpoint-specific error responses
        if response.get("error"):
            raise RuntimeError(f"API Error: {response['error']}")

        return {
            "data": MyResponse(**response["data"]),
            "resp": ResponseData(**response["resp"])
        }

    except (AuthError, M4300Error) as e:
        # Let authentication and retry errors propagate
        raise
    except Exception as e:
        # Handle or wrap other errors
        raise RuntimeError(f"Failed to call endpoint: {str(e)}") from e
```

## Testing

1. Create mock responses:
```python
@pytest.fixture
def mock_success_response():
    """Mock successful API response."""
    return {
        "data": {"key": "value"},
        "resp": {
            "status": "success",
            "respCode": 0,
            "respMsg": "Success"
        }
    }

def test_my_endpoint(mock_session, mock_success_response):
    """Test endpoint helper."""
    mock_response = Mock(ok=True)
    mock_response.json.return_value = mock_success_response
    mock_session.request.return_value = mock_response

    result = my_endpoint(
        base_url="https://192.168.1.1:8443",
        token="test_token",
        auth_callback=lambda: ("admin", "pass")
    )

    assert result["data"].key == "value"
    assert result["resp"].status == "success"
```

2. Test error cases:
```python
def test_my_endpoint_error(mock_session):
    """Test error handling."""
    mock_session.request.side_effect = requests.exceptions.Timeout()

    with pytest.raises(M4300Error, match="Request failed after 3 attempts"):
        my_endpoint(...)
```

## Best Practices

1. Type Safety
   - Use TypedDict for response structures
   - Add type hints to all parameters
   - Validate response data structure

2. Documentation
   - Document all parameters
   - Include response format
   - Add usage examples
   - Document error cases

3. Testing
   - Test happy path
   - Test error cases
   - Test retry behavior
   - Test with real API in integration tests

4. Error Handling
   - Handle endpoint-specific errors
   - Validate response format
   - Provide clear error messages
   - Preserve error context

5. Response Structure
   - Follow API result pattern
   - Use consistent naming
   - Include all response fields
   - Document any deviations
