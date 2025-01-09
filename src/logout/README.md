# Logout Helper

Helper module for interacting with the M4300 switch logout endpoint.

## Overview

This module provides a function to logout from a device and invalidate the authentication token. It handles all necessary validation and error cases.

## Usage

```python
from logout import logout

try:
    # Logout from device
    response = logout(
        base_url="https://192.168.99.92:8443",
        token="a11cd17543520ace80d7c7b45aba43357b4d0844995879364aa4d47b2671fe2e"
    )
    
    # Success response example:
    # {
    #     "logout": {},
    #     "resp": {
    #         "status": "success", 
    #         "respCode": 0,
    #         "respMsg": "Operation success"
    #     }
    # }
    
except ValueError as e:
    print(f"Invalid parameters: {e}")
except RuntimeError as e:
    print(f"Logout failed: {e}")
```

## Parameters

- `base_url` (str): Base URL of the API (e.g., https://192.168.99.92:8443)
- `token` (str): Authentication token obtained from login

## Returns

Dictionary containing the logout response with status information.

## Errors

- `ValueError`: If required parameters are missing or invalid
- `RuntimeError`: If the logout request fails or returns an invalid response
- `RequestException`: If there are network/connection issues

## API Details

- **Endpoint**: POST /api/v1/logout
- **Auth**: Bearer token required
- **Request Body**: Empty
- **Response**: JSON with status information

## Testing

Run the tests:
```bash
python -m pytest tests/test_logout.py
```

Integration tests require a live device:
```bash
python -m pytest tests/test_logout_integration.py
