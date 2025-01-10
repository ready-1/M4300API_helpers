# make_api_call Helper

## Overview

The make_api_call helper provides a centralized interface for all M4300 switch API communications. It handles authentication, retries, SSL verification, and comprehensive error handling while supporting all requests library features.

## Interface

```python
def make_api_call(
    method: str,
    url: str,
    token: str,
    auth_callback: Callable[[], tuple[str, str]],
    data: dict = None,
    params: dict = None,
    files: dict = None,
    headers: dict = None,
    cookies: dict = None,
    verify_ssl: bool = None,
    timeout: Union[float, tuple] = 30,
    max_retries: int = 3,
    allow_redirects: bool = True,
    stream: bool = False,
    proxies: dict = None
) -> tuple[dict, Optional[str]]:
    """
    Make an API call to the M4300 switch with automatic token refresh.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Complete URL from build_switch_url (includes /api/v1/)
        token: Current authentication token
        auth_callback: Function that returns (username, password) for token refresh
        data: Request payload for POST/PUT
        params: URL query parameters
        files: Files to upload
        headers: Additional headers (Authorization added automatically)
        cookies: Request cookies
        verify_ssl: SSL verification flag (default from M4300_SSL_VERIFY)
        timeout: Request timeout in seconds, or (connect, read) tuple
        max_retries: Maximum retry attempts for recoverable errors
        allow_redirects: Whether to follow redirects
        stream: Whether to stream the response
        proxies: Proxy configuration

    Returns:
        tuple[dict, Optional[str]]: (Response data, New token if refreshed)

    Raises:
        RequestException: For unrecoverable request errors
        ValueError: For invalid parameters
        AuthError: When authentication fails after retries
    """
```

## Authentication Flow

1. Normal Request:
```python
# First attempt with current token
headers = {'Authorization': f'Bearer {token}'}
response = requests.request(method, url, headers=headers, ...)

# If successful, return response
if response.ok:
    return response.json(), None
```

2. Token Refresh:
```python
# If 401 received
if response.status_code == 401:
    # Get credentials from callback
    username, password = auth_callback()

    # Login to get new token using /api/v1/login endpoint
    login_url = build_switch_url(hostname, "/login")  # Adds /api/v1/ prefix
    auth_response = requests.post(
        login_url,
        json={'username': username, 'password': password},
        verify=verify_ssl
    )
    new_token = auth_response.json()['token']

    # Retry original request with new token
    headers['Authorization'] = f'Bearer {new_token}'
    response = requests.request(method, url, headers=headers, ...)

    # Return response and new token
    return response.json(), new_token
```

## Error Handling

1. Retryable Errors:
- 401 Unauthorized (triggers token refresh)
- 408 Request Timeout
- 429 Too Many Requests
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout
- Network timeouts
- Connection errors

2. Non-Retryable Errors:
- 400 Bad Request
- 403 Forbidden
- 404 Not Found
- 405 Method Not Allowed
- Other 4xx errors
- Validation errors

## SSL Verification

1. Environment Configuration:
```bash
# In environment or .env file
M4300_SSL_VERIFY=true    # Enable verification (default)
M4300_SSL_VERIFY=false   # Disable verification
```

2. Per-Request Override:
```python
# Override environment setting
response, new_token = make_api_call(
    method="GET",
    url=url,
    token=token,
    auth_callback=get_creds,
    verify_ssl=False  # Disable for this request
)
```

## Usage Examples

1. Basic GET Request:
```python
def get_device_info(token: str) -> dict:
    # build_switch_url adds /api/v1/ prefix
    url = build_switch_url("192.168.1.1", "/device-info")
    # Returns: https://192.168.1.1:8443/api/v1/device-info

    response, new_token = make_api_call(
        method="GET",
        url=url,
        token=token,
        auth_callback=lambda: (session['username'], session['password'])
    )
    if new_token:
        session['token'] = new_token
    return response
```

2. File Upload:
```python
def upload_firmware(token: str, firmware_path: str) -> dict:
    url = build_switch_url("192.168.1.1", "/firmware/upload")
    # Returns: https://192.168.1.1:8443/api/v1/firmware/upload

    with open(firmware_path, 'rb') as f:
        response, new_token = make_api_call(
            method="POST",
            url=url,
            token=token,
            auth_callback=get_creds,
            files={'firmware': f},
            timeout=(5, 300)  # 5s connect, 5min read
        )
    return response
```

3. Error Handling:
```python
try:
    response, new_token = make_api_call(
        method="GET",
        url=url,  # URL already includes /api/v1/
        token=token,
        auth_callback=get_creds
    )
except requests.exceptions.RequestException as e:
    logger.error(f"Request failed: {e}")
    raise
```

## Testing Strategy

1. Authentication Tests:
- Valid token success
- Token refresh flow
- Invalid credentials
- Missing token
- Auth callback errors

2. Retry Logic:
- Network timeouts
- Server errors
- Rate limiting
- Connection issues
- Maximum retries

3. Request Features:
- Different HTTP methods
- File uploads
- Streaming responses
- Custom headers
- Query parameters

4. Error Handling:
- Non-retryable errors
- Network failures
- Invalid parameters
- SSL verification
- Timeout handling

5. Integration:
- Real switch communication
- Multiple endpoints
- Error scenarios
- Performance testing

## Implementation Notes

1. Security:
- No credential storage
- Token handling
- SSL verification
- Header sanitization

2. Performance:
- Connection pooling
- Efficient retries
- Resource cleanup
- Memory management

3. Maintainability:
- Clear error messages
- Comprehensive logging
- Clean separation of concerns
- Well-documented behavior

4. Reliability:
- Robust error handling
- Predictable retry behavior
- Resource cleanup
- State management
