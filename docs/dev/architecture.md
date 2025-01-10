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

## Centralized API Communication

### make_api_call Helper

The library implements a centralized API communication pattern through the `make_api_call()` helper function. This design consolidates all HTTP interactions into a single, well-tested component that ensures consistency across all endpoint implementations.

#### Core Responsibilities

1. **Connection Management**
   - Handle HTTP/HTTPS connections
   - Manage connection pooling
   - Implement timeout logic
   - Handle SSL/TLS configuration

2. **Authentication**
   - Manage authentication tokens
   - Handle token refresh
   - Implement retry logic for auth failures
   - Track session state

3. **Request Processing**
   - Standardize request formatting
   - Handle different HTTP methods
   - Manage headers consistently
   - Implement request validation

4. **Response Handling**
   - Standardize response parsing
   - Implement error detection
   - Handle different response types
   - Manage response validation

5. **Error Management**
   - Consistent error categorization
   - Standardized error responses
   - Detailed error logging
   - Retry logic for recoverable errors

#### SSL Warning Suppression

When working with self-signed certificates or development environments, SSL warnings can be suppressed using urllib3. The make_api_call() helper supports this through a dedicated flag:

```python
# At helper level
async def make_api_call(
    method: str,
    endpoint: str,
    suppress_ssl_warnings: bool = False,  # New parameter
    **kwargs
) -> ApiResponse:
    """
    Centralized API communication function that handles all HTTP interactions.

    Args:
        suppress_ssl_warnings: When True, disables urllib3 SSL warnings.
                             Use in development/testing only.
    """
    if suppress_ssl_warnings:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Proceed with request...
```

Usage examples:

1. **Development Environment**
```python
# SSL warnings suppressed for development
response = await make_api_call(
    method="GET",
    endpoint="/device/config",
    suppress_ssl_warnings=True  # Disable warnings
)
```

2. **Production Environment**
```python
# SSL warnings enabled for production (default)
response = await make_api_call(
    method="GET",
    endpoint="/device/config"
    # suppress_ssl_warnings defaults to False
)
```

#### Standard Formats

1. **Request Format**
```python
@dataclass
class ApiRequest:
    """Standard format for all API requests"""
    method: str                    # HTTP method (GET, POST, etc.)
    endpoint: str                  # API endpoint path
    data: Optional[Dict] = None    # Request body for POST/PUT
    params: Optional[Dict] = None  # URL query parameters
    headers: Optional[Dict] = None # Custom headers
    timeout: Optional[float] = None # Request timeout in seconds
```

2. **Response Format**
```python
@dataclass
class ApiResponse:
    """Standard format for all API responses"""
    status_code: int              # HTTP status code
    data: Dict                    # Response body data
    headers: Dict                 # Response headers
    error: Optional[str] = None   # Error message if any
    raw: Optional[bytes] = None   # Raw response data
```

3. **Error Format**
```python
@dataclass
class ApiError:
    """Standard format for API errors"""
    code: str                     # Error code (e.g., AUTH_FAILED)
    message: str                  # Human readable error message
    details: Optional[Dict] = None # Additional error details
    http_status: int              # Associated HTTP status code
```

#### Interface Design

```python
async def make_api_call(
    method: str,                 # HTTP method (GET, POST, etc.)
    endpoint: str,               # API endpoint path
    data: Optional[dict] = None, # Request payload
    params: Optional[dict] = None, # URL parameters
    headers: Optional[dict] = None, # Additional headers
    timeout: Optional[float] = None, # Request timeout
    retries: int = 3,           # Number of retry attempts
    validate: bool = True       # Enable response validation
) -> ApiResponse:               # Typed response object
    """
    Centralized API communication function that handles all HTTP interactions
    with the M4300 API endpoints.
    """
    pass
```

#### Practical Usage Example

Let's walk through how make_api_call() works in practice using a device configuration update:

1. **Endpoint Implementation**
```python
async def update_device_config(config: DeviceConfig) -> DeviceConfigResponse:
    """Update device configuration settings"""

    # 1. Input Validation
    validated_data = config.to_dict()  # Dataclass validates structure

    # 2. API Call
    response = await make_api_call(
        method="POST",
        endpoint="/device/config",
        data=validated_data,
        validate=True
    )

    # 3. Response Processing
    return DeviceConfigResponse.from_dict(response.data)
```

2. **What Happens Inside make_api_call()**

   a. **Request Preparation**
   ```python
   # Constructs ApiRequest object
   request = ApiRequest(
       method="POST",
       endpoint="/device/config",
       data=validated_data
   )

   # Adds auth headers
   request.headers["Authorization"] = f"Bearer {current_token}"
   ```

   b. **Error Handling & Retries**
   ```python
   for attempt in range(retries):
       try:
           response = await send_request(request)
           break
       except AuthError:
           # Auto-refresh token and retry
           await refresh_auth_token()
       except NetworkError:
           # Implement exponential backoff
           await backoff(attempt)
   ```

   c. **Response Processing**
   ```python
   # Constructs ApiResponse object
   api_response = ApiResponse(
       status_code=response.status,
       data=response.json(),
       headers=response.headers
   )

   # Validates response structure
   if validate:
       validate_response_schema(api_response)
   ```

3. **Error Scenarios**

   a. **Authentication Failure**
   ```python
   # Token expired
   response = await make_api_call(...)
   # -> Automatically refreshes token and retries
   # -> Returns ApiError if refresh fails
   ```

   b. **Network Issues**
   ```python
   # Connection timeout
   response = await make_api_call(...)
   # -> Implements exponential backoff
   # -> Retries up to configured limit
   ```

   c. **Validation Errors**
   ```python
   # Invalid response format
   response = await make_api_call(...)
   # -> Returns ApiError with validation details
   # -> Logs detailed error information
   ```

4. **Logging & Debugging**
```python
# Debug level logging
>>> Sending POST request to /device/config
>>> Headers: {"Authorization": "Bearer ***", ...}
>>> Payload: {"name": "switch1", ...}
>>> Response received: 200 OK
>>> Response data: {"status": "success", ...}
```

This centralized approach ensures:
- Consistent error handling across all endpoints
- Automatic token refresh and retry logic
- Standardized logging and debugging
- Type safety through dataclass validation
- Single source of truth for API communication

#### Migration Strategy

1. **Phase 1: Infrastructure**
   - Implement make_api_call() helper
   - Add comprehensive test suite
   - Document interface and behaviors
   - Create usage examples

2. **Phase 2: Initial Migration**
   - Convert one endpoint as proof of concept
   - Validate behavior matches original
   - Document migration process
   - Update testing approach

3. **Phase 3: Full Migration**
   - Systematically convert all endpoints
   - Update all tests
   - Verify no behavior changes
   - Update documentation

4. **Phase 4: Cleanup**
   - Remove duplicate code
   - Consolidate error handling
   - Update integration tests
   - Final documentation review

#### Implementation Components

1. **HTTP Client Selection**

The make_api_call() helper requires a robust HTTP client library. Key considerations:

a. **Library Options**
   - aiohttp: Modern async HTTP client
   - requests: Synchronous but widely used
   - httpx: Supports both sync/async

b. **Requirements**
   - SSL/TLS support with verification control
   - Connection pooling capabilities
   - Timeout configuration
   - Retry mechanisms
   - Header management
   - Session handling

c. **Configuration Parameters**
```python
HTTP_CLIENT_CONFIG = {
    "pool_connections": 100,     # Maximum connections in pool
    "pool_maxsize": 10,         # Maximum size per host
    "max_retries": 3,           # Default retry attempts
    "timeout": 30,              # Default timeout in seconds
    "ssl_verify": True,         # SSL verification default
    "cert_path": None,          # Custom cert path if needed
}
```

d. **Session Management**
```python
class ApiSession:
    """Manages HTTP client session and configuration"""
    def __init__(self, base_url: str, config: Dict):
        self.base_url = base_url
        self.config = {**HTTP_CLIENT_CONFIG, **config}
        self.session = None  # Initialized on first use

    async def get_session(self):
        """Returns existing session or creates new one"""
        if not self.session:
            self.session = await self._create_session()
        return self.session
```

2. **Retry and Timeout Configuration**

The helper implements sophisticated retry and timeout handling:

a. **Retry Configuration**
```python
RETRY_CONFIG = {
    "max_attempts": 3,          # Maximum retry attempts
    "initial_delay": 1.0,       # Initial delay in seconds
    "max_delay": 30.0,         # Maximum delay between retries
    "backoff_factor": 2.0,     # Exponential backoff multiplier
    "retry_on": [              # HTTP status codes to retry
        408,  # Request Timeout
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504   # Gateway Timeout
    ]
}
```

b. **Timeout Configuration**
```python
TIMEOUT_CONFIG = {
    "connect": 5.0,            # Connection timeout
    "read": 30.0,             # Read timeout
    "write": 30.0,            # Write timeout
    "pool": 5.0,              # Pool timeout
    "total": 60.0             # Total operation timeout
}
```

c. **Backoff Implementation**
```python
async def calculate_delay(attempt: int, config: Dict) -> float:
    """Calculate delay for retry attempt using exponential backoff"""
    delay = min(
        config["initial_delay"] * (config["backoff_factor"] ** attempt),
        config["max_delay"]
    )
    return delay + (random.random() * 0.1)  # Add jitter
```

d. **Usage in make_api_call()**
```python
async def make_api_call(...):
    for attempt in range(RETRY_CONFIG["max_attempts"]):
        try:
            return await _execute_request(...)
        except RetryableError as e:
            if attempt == RETRY_CONFIG["max_attempts"] - 1:
                raise
            delay = await calculate_delay(attempt, RETRY_CONFIG)
            logger.warning(f"Retry {attempt + 1} after {delay}s: {str(e)}")
            await asyncio.sleep(delay)
```

3. **Response Validation System**

The helper implements comprehensive response validation:

a. **Schema Definitions**
```python
@dataclass
class ResponseSchema:
    """Defines expected response structure"""
    required_fields: List[str]     # Must-have fields
    optional_fields: List[str]     # May-have fields
    field_types: Dict[str, Type]   # Expected types
    nested_schemas: Dict[str, 'ResponseSchema'] = None  # Sub-schemas
```

b. **Validation Rules**
```python
VALIDATION_RULES = {
    "strict_types": True,          # Enforce exact type matching
    "allow_extra_fields": False,   # Reject unknown fields
    "null_handling": "strict",     # null field handling
    "array_validation": {
        "check_types": True,       # Validate array item types
        "allow_empty": True,       # Allow empty arrays
        "max_items": None          # Maximum items (if any)
    }
}
```

c. **Schema Registry**
```python
RESPONSE_SCHEMAS = {
    "device_info": ResponseSchema(
        required_fields=["id", "name", "status"],
        optional_fields=["description", "location"],
        field_types={
            "id": str,
            "name": str,
            "status": str,
            "description": Optional[str],
            "location": Optional[str]
        }
    ),
    # Additional schemas...
}
```

d. **Validation Implementation**
```python
async def validate_response(
    response: ApiResponse,
    schema_name: str
) -> None:
    """Validates response against registered schema"""
    schema = RESPONSE_SCHEMAS[schema_name]

    # Check required fields
    missing = [f for f in schema.required_fields
               if f not in response.data]
    if missing:
        raise ValidationError(f"Missing fields: {missing}")

    # Validate types
    for field, value in response.data.items():
        expected_type = schema.field_types.get(field)
        if expected_type and not isinstance(value, expected_type):
            raise ValidationError(
                f"Invalid type for {field}: "
                f"expected {expected_type}, got {type(value)}"
            )

    # Handle nested validation
    if schema.nested_schemas:
        for field, nested_schema in schema.nested_schemas.items():
            if field in response.data:
                await validate_response(
                    response.data[field],
                    nested_schema
                )
```

4. **Authentication Management**

The helper implements robust authentication handling:

a. **Token Management**
```python
@dataclass
class AuthToken:
    """Authentication token management"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    created_at: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        """Check if token is expired with 30s buffer"""
        return time.time() > (self.created_at + self.expires_in - 30)
```

b. **Authentication State**
```python
class AuthState:
    """Manages authentication state"""
    def __init__(self):
        self.current_token: Optional[AuthToken] = None
        self.refresh_lock = asyncio.Lock()
        self._refresh_task: Optional[asyncio.Task] = None

    async def get_valid_token(self) -> AuthToken:
        """Returns valid token, refreshing if needed"""
        if not self.current_token or self.current_token.is_expired:
            async with self.refresh_lock:
                # Double check after acquiring lock
                if not self.current_token or self.current_token.is_expired:
                    self.current_token = await self._refresh_token()
        return self.current_token
```

c. **Token Refresh Logic**
```python
async def _refresh_token(self) -> AuthToken:
    """Refreshes authentication token"""
    try:
        response = await self._execute_refresh()
        return AuthToken(
            access_token=response["access_token"],
            token_type=response.get("token_type", "Bearer"),
            expires_in=response.get("expires_in", 3600)
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise AuthError("Failed to refresh authentication token")
```

d. **Integration with make_api_call()**
```python
async def make_api_call(...):
    """Ensures valid authentication for requests"""
    token = await auth_state.get_valid_token()
    headers = headers or {}
    headers["Authorization"] = f"{token.token_type} {token.access_token}"

    try:
        return await _execute_request(
            method=method,
            endpoint=endpoint,
            headers=headers,
            **kwargs
        )
    except AuthError:
        # Token might be invalidated
        auth_state.current_token = None
        raise
```

5. **Logging and Debugging System**

The helper implements comprehensive logging for troubleshooting:

a. **Log Configuration**
```python
LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "simple": {
            "format": "%(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "INFO"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "api.log",
            "formatter": "detailed",
            "level": "DEBUG"
        }
    },
    "loggers": {
        "api_helper": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}
```

b. **Request Logging**
```python
async def log_request(request: ApiRequest) -> None:
    """Log API request details at appropriate levels"""
    logger.info(f"API Request: {request.method} {request.endpoint}")
    logger.debug("Request Details:", extra={
        "headers": mask_sensitive_headers(request.headers),
        "params": request.params,
        "data": mask_sensitive_data(request.data)
    })
```

c. **Response Logging**
```python
async def log_response(response: ApiResponse) -> None:
    """Log API response with appropriate detail levels"""
    logger.info(f"API Response: {response.status_code}")
    if response.status_code >= 400:
        logger.error("API Error:", extra={
            "status": response.status_code,
            "error": response.error,
            "details": response.data
        })
    logger.debug("Response Details:", extra={
        "headers": response.headers,
        "data": mask_sensitive_data(response.data)
    })
```

d. **Debug Helpers**
```python
class ApiDebugger:
    """Helper class for debugging API interactions"""

    @contextmanager
    async def trace_request(self, request: ApiRequest):
        """Trace complete request lifecycle"""
        start_time = time.time()
        try:
            await log_request(request)
            yield
        finally:
            duration = time.time() - start_time
            logger.debug(f"Request completed in {duration:.2f}s")

    def dump_session_state(self) -> Dict:
        """Dump current session state for debugging"""
        return {
            "active_requests": self._active_requests,
            "auth_state": self._auth_state,
            "connection_pool": self._pool_stats()
        }
```

#### Testing Strategy

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
