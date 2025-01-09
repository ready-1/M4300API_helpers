# Logout Helper

Helper module for M4300 switch logout endpoint. Handles token invalidation and session cleanup.

## Quick Start

```python
from m4300api_helpers.logout import logout

# Logout and invalidate token
result = logout(
    base_url="https://192.168.99.92:8443",
    token="your_auth_token"
)
```

## Important Notes

1. API Response Format
   - API returns tab-indented JSON without commas
   - This is normal and handled by the implementation
   - Don't trust visual representation in logs/errors

2. Error Handling
   - All errors start with "API request failed:"
   - Includes specific error details after prefix
   - Handles both API and network errors

3. Response Structure
```python
{
    "logout": {},  # Empty object (future use)
    "resp": {
        "status": str,    # "success" or "failure"
        "respCode": int,  # Response code
        "respMsg": str    # Human-readable message
    }
}
```

## Common Issues

1. Display Artifacts
   - Error messages may show missing commas
   - This is a display issue, not a data issue
   - Use systematic verification to validate actual data

2. Error Messages
   - Must follow "API request failed:" pattern
   - Include specific error details
   - Match test expectations

## Testing

Run integration tests:
```bash
pytest -v --run-integration tests/test_logout_integration.py
```

## Documentation

- Full API details: [info_doc_logout.txt](../../../docs/dev/mcp_info/info_doc_logout.txt)
- Error handling: [systematic_verification.md](../../../docs/dev/systematic_verification.md)
