# Login Helper

Helper module for authenticating with the device API.

## Usage

```python
from src.login.login import login

# Initialize with device credentials
base_url = "https://192.168.99.92:8443"
username = "admin"
password = "password123"

try:
    # Attempt login
    result = login(base_url, username, password)
    
    # Extract auth token for subsequent requests
    auth_token = result["login"]["token"]
    token_expiry = result["login"]["expire"]
    
except ValueError as e:
    print(f"Invalid parameters: {e}")
except RuntimeError as e:
    print(f"Login failed: {e}")
```

## API Details

### Endpoint
`POST /api/v1/login`

### Parameters

- `base_url` (str): Base URL of the API (e.g., https://192.168.99.92:8443)
- `username` (str): Admin username
- `password` (str): Admin user's password

### Response Format

```json
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
```

### Error Handling

The helper handles various error cases:

- Missing/invalid parameters (ValueError)
- Network/connection errors (RuntimeError)
- Invalid credentials (RuntimeError)
- Malformed responses (RuntimeError)

### Tests

Comprehensive test suite covers:

- Successful login flow
- Parameter validation
- Error response handling
- Network error handling
- Response format validation

Run tests with pytest:
```bash
pytest tests/test_login.py -v
