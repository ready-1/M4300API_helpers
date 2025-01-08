# Architectural Document for Python API Helpers Library

## Overview

This library provides a Python interface for accessing the management API of Netgear switches. It is designed for integration with management front ends, primarily as the API interface for a Django application. The library implements synchronous operations with a focus on simplicity and reliability.

## Development MCP Server

The development process will be supported by a local MCP server to reduce Anthropic API costs and provide development assistance.

### MCP Server Features

1. **Documentation Access**
   - Load and serve M4300 API documentation
   - Provide quick endpoint reference lookups
   - Track documentation discrepancies

2. **Code Assistance**
   - Generate Python dataclass models
   - Provide code completion suggestions
   - Assist with input validation

3. **Development Tools**
   - Example code generation
   - Test case suggestions
   - Error case handling

### Implementation Timeline

1. **Basic Setup (1 hour)**
   - MCP server bootstrap
   - Documentation loading
   - Simple lookup endpoints

2. **Code Generation (1 hour)**
   - Dataclass generation
   - Code completion
   - Validation helpers

3. **Integration (1 hour)**
   - Cline extension integration
   - Error handling
   - Configuration

4. **Testing (1 hour)**
   - Validation and testing
   - Documentation
   - Example usage

---

## Endpoint Implementation Structure

Each API endpoint implementation follows a standardized structure:

```plaintext
endpoints/
├── login/
│   ├── sample_code.py      # Postman code examples
│   ├── response.json       # Sample API responses
│   ├── ref_docs.txt        # PDF documentation reference
│   ├── implementation.py   # Actual implementation
│   └── test_login.py       # Test cases
└── device_info/
    ├── sample_code.py
    └── ...
```

### Implementation Workflow

1. **Setup**
   - Create endpoint directory structure
   - Add sample code from Postman
   - Include real response data
   - Copy relevant documentation

2. **Development**
   - Document API discrepancies
   - Create dataclass models
   - Implement validation
   - Write unit tests

3. **Validation**
   - Run integration tests
   - Execute validation scripts
   - Update documentation
   - Commit changes

### Endpoint Organization

The library's endpoints are organized according to the API documentation sections, maintaining clear reference to the original documentation while providing a developer-friendly interface.

1. **Input Format**
   ```
   # Format: section_number,HTTP_METHOD,endpoint_name
   6.1,POST,snooping_vlan         # Section 6.1 in PDF
   6.2,GET,snooping_config        # Section 6.2 in PDF
   6.3,POST,snooping_config       # Section 6.3 in PDF
   ```

2. **Generated Structure**
   ```python
   # endpoints/6_multicast/snooping.py  # Section 6: Multicast
   def get_vlan():          # 6.1
   def get_config():        # 6.2
   def set_config():        # 6.3

   # endpoints/7_port_info/port.py      # Section 7: Port Information
   def get_config():        # 7.1
   def set_config():        # 7.2
   ```

3. **Benefits**
   - Direct mapping to API documentation sections
   - Logical grouping of related endpoints
   - Clear function naming with getter/setter pattern
   - Original endpoint references preserved in comments
   - Easy documentation cross-reference

4. **File Organization**
   ```plaintext
   endpoints/
   ├── 1_authentication/        # Section 1: Authentication
   │   └── auth.py
   ├── 2_device_settings/       # Section 2: Device Settings
   │   └── device.py
   ├── 6_multicast/            # Section 6: Multicast
   │   └── snooping.py
   └── 7_port_info/            # Section 7: Port Information
       └── port.py
   ```

---

## Key Features

1. **Modular Structure**
   - Simple API wrappers with input validation
   - Separate modules for different functional areas
   - Shared utilities through central request handler

2. **Authentication**
   - Basic auth for initial login
   - Bearer token auth for API calls
   - Session-based token management (per Switch instance)
   - Automatic retry with exponential backoff for auth failures

3. **Error Handling**
   - Input validation using dataclasses
   - Range/enum validation against API specs
   - Error returns rather than exceptions
   - Detailed error logging for debugging

4. **Configuration**
   - External config file (format TBD)
   - Environment variable overrides
   - Per-request config reloading
   - Configurable timeouts per endpoint

5. **Logging**
   - Centralized logging configuration
   - Console and file outputs
   - Syslog server support (future)
   - Debug level includes full request/response details
   - Info level includes operation summaries

6. **Response Handling**
   - Raw dictionary responses
   - Basic response validation
   - Error handling for unexpected formats

7. **Testing Strategy**
   - Both online and offline tests
   - Real switch integration tests (192.168.99.92)
   - Port 50 available for cable tests
   - Separate test flags for integration tests
   - Automated validation workflow

---

## Library Structure

```plaintext
api_helpers/
│
├── __init__.py        # Package initialization
├── switch.py          # Main Switch class implementation
├── request.py         # Centralized request handler
├── auth.py           # Authentication and token management
├── config.py         # Configuration management
├── validation.py     # Input validation using dataclasses
├── logging.py        # Logging configuration and setup
├── endpoints/        # API endpoint implementations
│   ├── __init__.py
│   ├── vlans.py
│   ├── ports.py
│   └── ...
├── tests/           # Test implementations
│   ├── __init__.py
│   ├── test_offline.py
│   ├── test_online.py
│   └── test_integration.py
└── scripts/         # Development and validation scripts
    ├── validate.sh
    └── run_tests.sh
