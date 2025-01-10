# make_api_call Helper

## Overview

The make_api_call() helper provides a centralized API communication pattern that consolidates all HTTP interactions into a single, well-tested component. This ensures consistency across all endpoint implementations.

## Core Responsibilities

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

## Implementation Components

### 1. HTTP Client Selection

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

### 2. Standard Data Formats

a. **Request Format**
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

b. **Response Format**
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

c. **Error Format**
```python
@dataclass
class ApiError:
    """Standard format for API errors"""
    code: str                     # Error code (e.g., AUTH_FAILED)
    message: str                  # Human readable error message
    details: Optional[Dict] = None # Additional error details
    http_status: int              # Associated HTTP status code
```

### 3. Retry and Timeout Configuration

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

### 4. Authentication Management

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

### 5. Logging and Debugging

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

b. **Debug Helpers**
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

## Interface Design

```python
async def make_api_call(
    method: str,                 # HTTP method (GET, POST, etc.)
    endpoint: str,               # API endpoint path
    data: Optional[dict] = None, # Request payload
    params: Optional[dict] = None, # URL parameters
    headers: Optional[dict] = None, # Additional headers
    timeout: Optional[float] = None, # Request timeout
    retries: int = 3,           # Number of retry attempts
    validate: bool = True,      # Enable response validation
    suppress_ssl_warnings: bool = False  # Suppress SSL warnings in dev
) -> ApiResponse:               # Typed response object
    """
    Centralized API communication function that handles all HTTP interactions
    with the M4300 API endpoints.
    """
    pass
```

## Usage Example

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

## Testing Strategy

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

## Implementation Plan

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
