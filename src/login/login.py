"""Helper module for login endpoint interactions."""
import json
from typing import Dict, Any
import urllib3
import requests
from requests.exceptions import RequestException

# Disable only the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def login(base_url: str, username: str, password: str) -> Dict[str, Any]:
    """Login to device and obtain authentication token.
    
    Args:
        base_url: Base URL of the API (e.g., https://192.168.99.92:8443)
        username: Admin username
        password: Admin user's password
        
    Returns:
        Dict containing login response with auth token and expiration
        Example:
        {
            "login": {
                "token": "8c523ad44e0a8f46324aa71f371963e07211b04b7239519a6f60f1ee5939dcc0b1db6b49394ff6866a67c45a396993f9a21359c3abe595821f579cfd25fafeeb",
                "expire": "86400"
            },
            "resp": {
                "status": "success",
                "respCode": 0,
                "respMsg": "Operation success"
            }
        }
        
    Raises:
        ValueError: If required parameters are missing or invalid
        RequestException: If API request fails
        RuntimeError: If login fails or response is invalid
    """
    # Validate input parameters
    if not base_url:
        raise ValueError("base_url is required")
    if not username:
        raise ValueError("username is required")
    if not password:
        raise ValueError("password is required")
        
    url = f"{base_url}/api/v1/login"
    
    payload = {
        "login": {
            "username": username,
            "password": password
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        response.raise_for_status()  # Raises HTTPError for bad responses
        
        try:
            data = response.json()
            # Check for error response first
            if data.get("resp", {}).get("status") == "failure":
                raise RuntimeError(f"Login failed: {data['resp']['respMsg']}")
            
            # Then validate response structure
            if not data.get("login", {}).get("token") or "status" not in data.get("resp", {}):
                raise RuntimeError("Invalid response format")
            
            return data
        except json.JSONDecodeError:
                # Handle non-JSON responses (like plain text error messages)
                error_text = response.text.strip()
                # All plain text responses are login failures
                raise RuntimeError(f"Login failed: {error_text}")
        
    except RequestException as e:
        raise RuntimeError(f"API request failed: {str(e)}")
