# build_switch_url Helper

## Overview

The build_switch_url helper constructs properly formatted URLs for M4300 switch API endpoints. It handles protocol selection, port configuration, and path normalization to ensure consistent URL formatting across all API calls.

## Interface

```python
def build_switch_url(
    hostname: str,
    endpoint: str,
    port: int = 8443
) -> str:
    """
    Build a complete URL for M4300 switch API endpoints.

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
```

## Behavior

1. Protocol Handling:
   - Always uses HTTPS
   - No HTTP support for security

2. Hostname Processing:
   - Accepts IP addresses or hostnames
   - Strips any existing protocol prefix
   - Validates basic hostname format
   - No DNS resolution

3. Port Management:
   - Default port 8443
   - Configurable per call
   - Validates port range

4. Path Normalization:
   - Adds /api/v1/ prefix
   - Handles leading/trailing slashes
   - Normalizes multiple slashes
   - Preserves query parameters

## Examples

```python
# Basic usage
url = build_switch_url("192.168.1.1", "/device-info")
# Returns: https://192.168.1.1:8443/api/v1/device-info

# Custom port
url = build_switch_url("switch.local", "/login", port=443)
# Returns: https://switch.local:443/api/v1/login

# Path normalization
url = build_switch_url("10.0.0.1", "status/")
# Returns: https://10.0.0.1:8443/api/v1/status

# With query parameters
url = build_switch_url("192.168.1.1", "/config?type=network")
# Returns: https://192.168.1.1:8443/api/v1/config?type=network
```

## Error Handling

1. Invalid Hostname:
```python
# Empty hostname
build_switch_url("", "/status")
# Raises ValueError("Hostname cannot be empty")

# Invalid characters
build_switch_url("switch@domain", "/status")
# Raises ValueError("Invalid hostname format")
```

2. Invalid Endpoint:
```python
# Empty endpoint
build_switch_url("192.168.1.1", "")
# Raises ValueError("Endpoint cannot be empty")

# Invalid characters
build_switch_url("192.168.1.1", "/config\0")
# Raises ValueError("Invalid endpoint format")
```

3. Invalid Port:
```python
# Port out of range
build_switch_url("192.168.1.1", "/status", port=70000)
# Raises ValueError("Port must be between 1 and 65535")
```

## Testing Strategy

1. Basic Functionality:
   - Standard hostname/endpoint combinations
   - Different port numbers
   - Various path formats
   - API version prefix handling

2. Input Validation:
   - Invalid hostnames
   - Malformed endpoints
   - Invalid ports
   - Edge cases

3. Path Normalization:
   - Multiple slashes
   - Missing slashes
   - Query parameters
   - Special characters
   - API version prefix handling

4. Integration:
   - Use with make_api_call
   - Real switch URLs
   - Common endpoints

## Implementation Notes

1. Security:
   - No protocol override
   - Strict input validation
   - Safe character handling
   - Consistent API version

2. Performance:
   - Minimal string operations
   - No network operations
   - Quick validation checks
   - Efficient path handling

3. Maintainability:
   - Clear error messages
   - Documented constraints
   - Easy to modify defaults
   - Version prefix constant
