"""HTTP helper functions for M4300 switch API communication."""

import os
import re
import time
from typing import Optional, Callable, Union, Dict, Any, Tuple
from urllib.parse import urlparse, urljoin

import requests

from .login import login


class AuthError(Exception):
    """Raised when authentication fails after retries."""


class M4300Error(Exception):
    """Base class for M4300 API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize error with message and optional status code."""
        super().__init__(message)
        self.status_code = status_code


def make_api_call(
    method: str,
    url: str,
    token: str,
    auth_callback: Callable[[], tuple[str, str]],
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    cookies: Optional[Dict[str, Any]] = None,
    verify_ssl: Optional[bool] = None,
    timeout: Union[float, Tuple[float, float]] = 30,
    max_retries: int = 3,
    allow_redirects: bool = True,
    stream: bool = False,
    proxies: Optional[Dict[str, str]] = None,
) -> Tuple[Dict[str, Any], Optional[str]]:
    """Make an API call to the M4300 switch with automatic token refresh.

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
        M4300Error: For API-specific errors
    """
    # Handle SSL verification
    if verify_ssl is None:
        verify_ssl = os.getenv("M4300_SSL_VERIFY", "true").lower() == "true"

    # Prepare headers
    request_headers = {"Authorization": f"Bearer {token}"}
    if headers:
        request_headers.update(headers)

    # List of retryable status codes
    retryable_codes = {401, 408, 429, 500, 502, 503, 504}

    session = requests.Session()
    if proxies:
        session.proxies.update(proxies)

    new_token = None
    attempt = 0
    while attempt < max_retries:
        try:
            response = session.request(
                method=method,
                url=url,
                headers=request_headers,
                data=data,
                params=params,
                files=files,
                cookies=cookies,
                verify=verify_ssl,
                timeout=timeout,
                allow_redirects=allow_redirects,
                stream=stream,
            )

            # Handle 401 by refreshing token
            if response.status_code == 401 and attempt < max_retries - 1:
                username, password = auth_callback()
                hostname = urlparse(url).netloc.split(":")[0]
                base_url = f"https://{hostname}:8443"

                try:
                    # Use login helper to refresh token
                    login_result = login(base_url, username, password)
                    new_token = login_result["data"]["token"]
                    request_headers["Authorization"] = f"Bearer {new_token}"
                    attempt += 1
                    continue
                except (RuntimeError, ValueError) as e:
                    raise AuthError("Failed to refresh authentication token") from e

            # Handle other retryable errors
            if response.status_code in retryable_codes and attempt < max_retries - 1:
                attempt += 1
                time.sleep(min(2**attempt, 10))  # Exponential backoff
                continue

            # Handle non-retryable errors
            response.raise_for_status()

            # Return the response data and new token if one was obtained
            return response.json(), new_token

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                attempt += 1
                time.sleep(min(2**attempt, 10))
                continue
            raise M4300Error(f"Request failed after {max_retries} attempts")

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1 and isinstance(
                e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)
            ):
                attempt += 1
                time.sleep(min(2**attempt, 10))
                continue
            raise

    raise M4300Error(f"Request failed after {max_retries} attempts")


def build_switch_url(hostname: str, endpoint: str, port: int = 8443) -> str:
    """Build a complete URL for M4300 switch API endpoints.

    Args:
        hostname: Switch hostname or IP address
        endpoint: API endpoint path (without /api/v1 prefix)
        port: Switch API port (default: 8443)

    Returns:
        str: Complete URL with protocol, host, port, and path

    Raises:
        ValueError: If hostname or endpoint is invalid

    Example:
        >>> build_switch_url("192.168.1.1", "/device-info")
        'https://192.168.1.1:8443/api/v1/device-info'
    """
    # Validate hostname
    if not hostname:
        raise ValueError("Hostname cannot be empty")

    # Strip any existing protocol
    hostname = re.sub(r"^https?://", "", hostname)

    # Basic hostname validation (IP or hostname format)
    if not re.match(r"^[a-zA-Z0-9.-]+$", hostname):
        raise ValueError("Invalid hostname format")

    # Validate endpoint
    if not endpoint:
        raise ValueError("Endpoint cannot be empty")

    # Validate endpoint characters
    if not re.match(r"^[a-zA-Z0-9/._?=&-]+$", endpoint):
        raise ValueError("Invalid endpoint format")

    # Validate port range
    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535")

    # Construct base URL with port
    base_url = f"https://{hostname}:{port}"

    # Normalize endpoint path
    endpoint = endpoint.strip("/")
    api_path = f"/api/v1/{endpoint}"

    # Join URL parts safely
    return urljoin(base_url, api_path)
