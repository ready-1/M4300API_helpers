"""Helper module for M4300 switch logout endpoint.

This module provides functionality to logout from an M4300 switch and
invalidate the current authentication token.

Notes:
    1. SSL certificate verification is disabled as M4300 switches use
       self-signed certificates. This is a known and accepted limitation
       of the device's firmware.
       
    2. The M4300 API returns JSON responses that may appear to have missing
       commas in test output. This is a display artifact only - the JSON is
       valid and parsed correctly. See docs/dev/systematic_verification.md
       section "M4300 API Response Format" for details.
"""
import json
from typing import TypedDict, Literal
import requests
from requests.exceptions import RequestException

class ResponseData(TypedDict):
    status: Literal["success", "failure"]
    respCode: int
    respMsg: str

class LogoutResult(TypedDict):
    logout: dict[str, None]  # Empty object for future use
    resp: ResponseData


# Default timeout for API requests (in seconds)
DEFAULT_TIMEOUT = 10

def logout(base_url: str, token: str) -> LogoutResult:
    """Logout from M4300 switch and invalidate authentication token.
    
    Args:
        base_url: Base URL of the API (e.g., https://192.168.99.92:8443)
        token: Authentication token from login
        
    Returns:
        Dictionary containing the logout response:
        {
            "logout": {},
            "resp": {
                "status": str,  # "success" or "failure"
                "respCode": int,
                "respMsg": str
            }
        }
        
    Raises:
        ValueError: If required parameters are missing
        RuntimeError: If logout fails or returns invalid response
    """
    # Validate required parameters
    if not base_url:
        raise ValueError("base_url is required")
    if not token:
        raise ValueError("token is required")
        
    # Prepare request
    url = f"{base_url}/api/v1/logout"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Send request
    try:
        # SSL verification disabled for M4300's self-signed certificates
        response = requests.post(
            url,
            headers=headers,
            verify=False,  # nosec B501 - M4300 uses self-signed certificates
            timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()  # Raises HTTPError for bad responses
        
        try:
            # Parse response
            data = response.json()
            
            # Validate response format
            if not isinstance(data, dict):
                raise RuntimeError("Logout failed: Invalid response type")
            
            if "resp" not in data:
                raise RuntimeError("Logout failed: Missing response data")
                
            if "status" not in data["resp"]:
                raise RuntimeError("Logout failed: Missing status")
                
            # Check for error response
            if data["resp"]["status"] != "success":
                msg = data["resp"].get("respMsg", "Unknown error")
                raise RuntimeError(f"Logout failed: {msg}")
                
            # Cast response to correct type
            return LogoutResult(
                logout=dict(),  # Empty object as specified in API
                resp=dict(
                    status=data["resp"]["status"],
                    respCode=data["resp"]["respCode"],
                    respMsg=data["resp"]["respMsg"]
                )
            )
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Logout failed: Invalid JSON response")
        except (KeyError, TypeError) as e:
            raise RuntimeError(f"Logout failed: Invalid response format")
            
    except RequestException as e:
        raise RuntimeError(f"Logout failed: {str(e)}")
