"""Helper module for M4300 switch login endpoint.

This module provides functionality to login to an M4300 switch and obtain
an authentication token for subsequent API calls.

Note:
    SSL certificate verification is disabled as M4300 switches use
    self-signed certificates. This is a known and accepted limitation
    of the device's firmware.
"""
import json
from typing import TypedDict, Literal
import requests
from requests.exceptions import RequestException

class LoginResponse(TypedDict):
    token: str
    expire: str

class ResponseData(TypedDict):
    status: Literal["success", "failure"]
    respCode: int
    respMsg: str

class LoginResult(TypedDict):
    login: LoginResponse
    resp: ResponseData

# Default timeout for API requests (in seconds)
DEFAULT_TIMEOUT = 10

def login(base_url: str, username: str, password: str) -> LoginResult:
    """Login to M4300 switch and obtain authentication token.
    
    Args:
        base_url: Base URL of the API (e.g., https://192.168.99.92:8443)
        username: Admin username
        password: Admin user's password
        
    Returns:
        Dictionary containing the login response with token:
        {
            "login": {
                "token": str,  # Auth token for subsequent requests
                "expire": str  # Token expiration in seconds
            },
            "resp": {
                "status": str,  # "success" or "failure"
                "respCode": int,
                "respMsg": str
            }
        }
        
    Raises:
        ValueError: If required parameters are missing
        RuntimeError: If login fails or returns invalid response
    """
    # Validate required parameters
    if not base_url:
        raise ValueError("base_url is required")
    if not username:
        raise ValueError("username is required")
    if not password:
        raise ValueError("password is required")
        
    # Prepare request
    url = f"{base_url}/api/v1/login"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "login": {
            "username": username,
            "password": password
        }
    }
    
    # Send request
    try:
        # SSL verification disabled for M4300's self-signed certificates
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            verify=False,  # nosec B501 - M4300 uses self-signed certificates
            timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()  # Raises HTTPError for bad responses
        
        # Parse response
        data = response.json()
        
        # Validate response format
        if not all(key in data for key in ["login", "resp"]):
            raise RuntimeError("Invalid response format")
            
        # Check for error response
        if "status" not in data["resp"] or data["resp"]["status"] != "success":
            msg = data["resp"].get("respMsg", "Unknown error")
            raise RuntimeError(f"Login failed: {msg}")
            
        # Cast response to correct type
        return LoginResult(
            login=dict(token=data["login"]["token"], expire=data["login"]["expire"]),
            resp=dict(
                status=data["resp"]["status"],
                respCode=data["resp"]["respCode"],
                respMsg=data["resp"]["respMsg"]
            )
        )
        
    except json.JSONDecodeError:
        raise RuntimeError("Login failed: Invalid JSON response")
    except RequestException as e:
        raise RuntimeError(f"API request failed: {str(e)}")
