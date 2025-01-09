"""Helper module for logout endpoint interactions."""
import json
from typing import Dict, Any
import urllib3
import requests
from requests.exceptions import RequestException

# Disable only the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def logout(base_url: str, token: str) -> Dict[str, Any]:
    """Logout from device and invalidate authentication token.
    
    Args:
        base_url: Base URL of the API (e.g., https://192.168.99.92:8443)
        token: Authentication token from login
        
    Returns:
        Dict containing logout response
        Example:
        {
            "logout": {},
            "resp": {
                "status": "success",
                "respCode": 0,
                "respMsg": "Operation success"
            }
        }
        
    Raises:
        ValueError: If required parameters are missing or invalid
        RequestException: If API request fails
        RuntimeError: If logout fails or response is invalid
    """
    # Validate input parameters
    if not base_url:
        raise ValueError("base_url is required")
    if not token:
        raise ValueError("token is required")
        
    url = f"{base_url}/api/v1/logout"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url, headers=headers, verify=False)
        response.raise_for_status()  # Raises HTTPError for bad responses
        
        try:
            data = response.json()
            # Check for error response first
            if data.get("resp", {}).get("status") == "failure":
                raise RuntimeError(f"Logout failed: {data['resp']['respMsg']}")
            
            # Then validate response structure
            if "logout" not in data or "status" not in data.get("resp", {}):
                raise RuntimeError("Invalid response format")
            
            return data
        except json.JSONDecodeError:
            # Handle non-JSON responses (like plain text error messages)
            error_text = response.text.strip()
            # All plain text responses are logout failures
            raise RuntimeError(f"Logout failed: {error_text}")
        
    except RequestException as e:
        raise RuntimeError(f"API request failed: {str(e)}")
