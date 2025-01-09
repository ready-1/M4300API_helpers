"""Helper module for M4300 switch logout endpoint.

This module provides functionality to logout from an M4300 switch and
invalidate the current authentication token.

Note:
    SSL certificate verification is disabled as M4300 switches use
    self-signed certificates. This is a known and accepted limitation
    of the device's firmware.
"""
import json
from typing import Dict
import requests
from requests.exceptions import RequestException

# Default timeout for API requests (in seconds)
DEFAULT_TIMEOUT = 10

def logout(base_url: str, token: str) -> Dict:
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
            url=url,
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
                raise RuntimeError(f"API request failed: Invalid response type")
            
            if "resp" not in data:
                raise RuntimeError(f"API request failed: Missing response data")
                
            if "status" not in data["resp"]:
                raise RuntimeError(f"API request failed: Missing status")
                
            # Check for error response
            if data["resp"]["status"] != "success":
                msg = data["resp"].get("respMsg", "Unknown error")
                raise RuntimeError(f"API request failed: {msg}")
                
            return data
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise RuntimeError(f"API request failed: Invalid response format - {str(e)}")
            
    except RequestException as e:
        raise RuntimeError(f"API request failed: {str(e)}")
