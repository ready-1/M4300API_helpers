# M4300API Helpers

Python helper library for accessing the NetGear M4300 Switch API. This library provides a clean, Pythonic interface to the M4300 switch's REST API, with features like automatic token management, rate limiting, and comprehensive error handling.

## Features

- Full coverage of M4300 switch API endpoints
- Automatic token management and refresh
- Rate limiting protection
- Comprehensive error handling
- Type hints throughout
- 100% test coverage
- Async support for improved performance
- Extensive documentation

## Installation

```bash
pip install m4300api-helpers
```

## Basic Usage

```python
from m4300api_helpers import M4300Config, M4300Client
from m4300api_helpers.exceptions import M4300Error

# Configure from environment variables
config = M4300Config.from_env()

# Or configure manually
config = M4300Config(
    host="switch.example.com",
    username="admin",
    password="password"
)

# Create client
client = M4300Client(config)

try:
    # Get device information
    device_info = client.get("device_info")
    print(f"Switch Model: {device_info['device_info']['model']}")
    print(f"Firmware Version: {device_info['device_info']['swVer']}")
    
    # Configure a VLAN
    client.post("swcfg_vlan", params={"vlanid": 100}, json={
        "switchConfigVlan": {
            "vlanId": 100,
            "name": "Engineering",
            "voiceVlanState": False,
            "autoVoipState": False,
            "autoVideoState": False,
            "igmpConfig": {
                "igmpState": False
            }
        }
    })
    
except M4300Error as e:
    print(f"API Error: {e}")
```

## Configuration

The library can be configured either through environment variables or programmatically:

### Environment Variables

- `M4300_HOST`: Switch hostname or IP address
- `M4300_USERNAME`: Username for authentication
- `M4300_PASSWORD`: Password for authentication
- `M4300_PORT`: HTTPS port number (default: 8443)
- `M4300_VERIFY_SSL`: Whether to verify SSL certificates (default: true)
- `M4300_TIMEOUT`: Request timeout in seconds (default: 30)
- `M4300_RATE_LIMIT`: Maximum requests per second (default: 10)
- `M4300_TOKEN_REFRESH_MARGIN`: Seconds before token expiry to refresh (default: 300)

### Programmatic Configuration

```python
from m4300api_helpers import M4300Config

config = M4300Config(
    host="switch.example.com",
    username="admin",
    password="password",
    port=8443,
    verify_ssl=True,
    timeout=30,
    rate_limit=10,
    token_refresh_margin=300
)
```

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/M4300API_helpers.git
cd M4300API_helpers
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Set up pre-commit hooks:
```bash
poetry run pre-commit install
```

5. Run tests:
```bash
poetry run pytest
```

## Project Structure

```
m4300api_helpers/
├── src/
│   └── m4300api_helpers/
│       ├── auth_helpers/      # Authentication and token management
│       ├── device_helpers/    # Device settings and information
│       ├── diagnostics_helpers/ # Diagnostic tools
│       ├── lag_helpers/       # Link Aggregation Group settings
│       ├── logging_helpers/   # Logging configuration
│       ├── multicast_helpers/ # Multicast settings
│       ├── port_helpers/      # Port configuration
│       ├── poe_helpers/       # Power over Ethernet settings
│       ├── qos_helpers/       # Quality of Service settings
│       ├── routing_helpers/   # Routing configuration
│       ├── stp_helpers/       # Spanning Tree Protocol settings
│       ├── vlan_helpers/      # VLAN configuration
│       ├── client.py          # Base API client
│       ├── config.py          # Configuration management
│       └── exceptions.py      # Custom exceptions
└── tests/                     # Test suite
    ├── unit/                 # Unit tests
    ├── integration/          # Integration tests
    └── fixtures/             # Test fixtures
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details
