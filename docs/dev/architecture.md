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

## Core Components

### API Communication

The library uses a centralized API communication pattern through the `make_api_call()` helper function. This design consolidates all HTTP interactions into a single, well-tested component. See [make_api_call documentation](components/make_api_call.md) for detailed implementation.

Key features:
- Centralized request handling
- Consistent error management
- Standardized data formats
- Robust authentication
- Comprehensive logging

Benefits:
- Reduced code duplication
- Consistent behavior
- Simplified maintenance
- Better error handling
- Easier testing

1. **Unit Tests**
   - Core helper function testing
   - Error handling verification
   - Authentication flows
   - Retry logic

2. **Integration Tests**
   - Live API communication
   - Error condition handling
   - Performance validation
   - Cross-endpoint behavior

3. **Migration Tests**
   - Behavior comparison tests
   - Response validation
   - Error handling verification
   - Performance impact checks

---

## Testing Strategy

### Systematic Verification Method

The project uses a systematic verification approach for diagnosing issues and preventing cascading failures. This method is documented in detail in [systematic_verification.md](systematic_verification.md) and consists of:

1. **Structure Verification**
   - Verify data structures before behavior
   - Use Python's type system
   - Validate actual operations

2. **Behavior Verification**
   - Test operations before display
   - Verify serialization
   - Check actual functionality

3. **Function Verification**
   - Test actual function behavior
   - Verify return types
   - Check expected states

4. **Error Handling**
   - Verify error conditions
   - Test error messages
   - Validate error types

5. **External System Verification**
   - Test raw API responses
   - Verify network behavior
   - Check system integration

This approach prevents:
- Cascading failures from incorrect assumptions
- Fixes based on display artifacts
- Unnecessary code changes

### Testing Levels

1. **Unit Tests**
   - Both online and offline tests
   - Real switch integration tests (192.168.99.92)
   - Port 50 available for cable tests
   - Separate test flags for integration tests
   - Automated validation workflow

2. **Integration Tests**
   - Live switch testing
   - Cross-firmware checks
   - System integration
   - Example validation

3. **Validation Tests**
   - Input validation
   - Response validation
   - Error handling
   - Edge cases

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

---

## Endpoint Development Workflow

### Overview
The development of each endpoint follows a structured workflow that ensures reliability, maintainability, and knowledge preservation.

### Core Components

1. Information Management
   - Raw endpoint documentation in docs/dev/mcp_info/
   - MCP server as knowledge base
   - Python implementation in src/
   - Test suite validation

2. Development Process
   ```
   Input (Documentation)        Process                    Output (Implementation)
   │                           │                          │
   ├─ Postman example          │                         ├─ Working helper
   ├─ PDF documentation    ───>│ Knowledge ──> Code ──> Test ├─ Documentation
   ├─ Known quirks             │     ▲          │           ├─ Tests
   ├─ Live testing            │     └──────────┘           ├─ Examples
                              │    (Learning Loop)          │
   ```

### Workflow Phases

1. Information Gathering
   - Store raw documentation in standard format
   - Document working examples
   - Note known issues/quirks
   - Reference PDF sections

2. Knowledge Capture
   - Parse into MCP server
   - Track confidence levels
   - Document discrepancies
   - Store working examples

3. Implementation
   - Generate Python code
   - Add type hints
   - Write tests
   - Handle edge cases

4. Verification
   - Test against live switch
   - Update documentation
   - Record findings
   - Commit changes

### Quality Standards

1. Documentation
   - Standard format in mcp_info/
   - Clear confidence levels
   - Known issues documented
   - Examples preserved

2. Implementation
   - Type safety
   - Error handling
   - Test coverage
   - Edge cases

3. Verification
   - Live switch testing
   - Cross-firmware checks
   - Integration tests
   - Example validation
