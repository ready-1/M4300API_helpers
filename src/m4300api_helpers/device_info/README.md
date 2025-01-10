# Device Info Helper

Helper module for M4300 switch device information endpoint. Retrieves detailed device status including hardware details, operational metrics, and sensor readings.

## Quick Start

```python
from m4300api_helpers.device_info import get_device_info

# Get device information
result = get_device_info(
    base_url="https://192.168.99.92:8443",
    token="your_auth_token"
)

# Access device details
print(f"Model: {result['deviceInfo']['model']}")
print(f"Firmware: {result['deviceInfo']['swVer']}")
print(f"Uptime: {result['deviceInfo']['upTime']}")

# Check temperature sensors
for sensor in result['deviceInfo']['temperatureSensors']:
    print(f"{sensor['sensorDesc']}: {sensor['sensorTemp']}°C")
```

## Response Structure
```python
{
    "deviceInfo": {
        "serialNumber": str,    # Switch Serial Number
        "macAddr": str,         # Switch MAC Address
        "model": str,           # Switch Model Number
        "swVer": str,          # Active firmware version
        "numOfPorts": int,      # Total available ports
        "numOfActivePorts": int,# Currently active ports
        "memoryUsage": str,     # Memory usage percentage
        "cpuUsage": str,       # CPU usage percentage
        "fanState": [          # Fan status dictionary
            {"FAN-1": str}     # Fan name to state mapping
        ],
        "poeState": bool,      # PoE enabled status
        "upTime": str,         # Device uptime
        "temperatureSensors": [  # Temperature readings
            {
                "sensorNum": int,   # Sensor SKU
                "sensorDesc": str,   # Sensor description
                "sensorTemp": int,   # Temperature in Celsius
                "sensorState": int   # Operational state (0-6)
            }
        ],
        "bootVersion": str,    # Bootcode version
        "rxData": int,         # Total bytes received
        "txData": int          # Total bytes transmitted
    },
    "resp": {
        "status": str,         # "success" or "failure"
        "respCode": int,       # Response code
        "respMsg": str         # Response message
    }
}
```

## Temperature Sensor States
```python
0 = NONE
1 = NORMAL
2 = WARNING
3 = CRITICAL
4 = SHUTDOWN
5 = NOT PRESENT
6 = NOT OPERATIONAL
```

## Error Handling

1. Network Errors:
   ```python
   try:
       result = get_device_info(base_url, token)
   except RuntimeError as e:
       if "Connection refused" in str(e):
           print("Switch not accessible")
       elif "timeout" in str(e):
           print("Request timed out")
   ```

2. Response Validation:
   ```python
   try:
       result = get_device_info(base_url, token)
   except RuntimeError as e:
       if "Invalid response format" in str(e):
           print("Unexpected response structure")
       elif "Invalid token" in str(e):
           print("Authentication failed")
   ```

## Testing

Run unit tests:
```bash
pytest tests/test_device_info.py -v
```

Run integration tests:
```bash
pytest tests/test_device_info_integration.py -v --run-integration
```

## Documentation

- Full API details: [info_doc_GET_device_info.txt](../../../docs/dev/mcp_info/info_doc_GET_device_info.txt)
- Error handling: [systematic_verification.md](../../../docs/dev/systematic_verification.md)
