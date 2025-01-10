# Login Endpoint Helper

Implementation of the authentication endpoint for M4300 switches.

## Overview

This helper provides a type-safe interface for authenticating with M4300 switches and obtaining access tokens for subsequent API calls.

### PDF Documentation Reference
- Section 1.1: POST /login
- Page: Authentication and Security

## Usage

```python
from src.login.login import login

# Initialize with device credentials
try:
    result = login(
        base_url="https://192.168.99.92:8443",
        username="admin",
        password="password123"
    )

    # Extract token for subsequent requests
    auth_token = result["login"]["token"]
    token_expiry = result["login"]["expire"]  # in seconds (86400 = 24 hours)

except ValueError as e:
    print(f"Invalid parameters: {e}")
except RuntimeError as e:
    print(f"Login failed: {e}")
```

## API Details

### Endpoint
`POST /api/v1/login`

### Request Format
```json
{
  "login": {
    "username": "admin",
    "password": "password123"
  }
}
```

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

## Error Handling

### Input Validation
- Missing base URL: ValueError("base_url is required")
- Missing username: ValueError("username is required")
- Missing password: ValueError("password is required")

### API Errors
- Invalid credentials: RuntimeError("Login failed: Bad credentials...")
- Rate limiting: RuntimeError("Login failed: Maximum of five login attempts...")
- Network errors: RuntimeError("API request failed: [error details]")
- Invalid responses: RuntimeError("Invalid response format")

## Testing

### Unit Tests
Basic functionality tests with mocked responses:
```bash
python -m pytest tests/test_login.py -v
```

### Integration Tests
Live switch testing (requires test switch access):
```bash
python -m pytest tests/test_login_integration.py -v
```

## Known Issues & Limitations

1. SSL Verification
   - Switch uses self-signed certificates
   - SSL verification disabled by default
   - Warning messages suppressed for cleaner output

2. Rate Limiting
   - Maximum 5 login attempts within 5 minutes
   - Returns plain text error message
   - Requires waiting period before retry

3. Response Format
   - Success responses are JSON formatted
   - Error responses may be plain text
   - All error responses wrapped in RuntimeError
