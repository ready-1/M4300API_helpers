"""Exceptions for the M4300 API Helper library."""

class M4300Error(Exception):
    """Base exception for M4300 API Helper library."""
    pass

class AuthenticationError(M4300Error):
    """Raised when authentication fails."""
    pass

class TokenExpiredError(AuthenticationError):
    """Raised when the authentication token has expired."""
    pass

class InvalidCredentialsError(AuthenticationError):
    """Raised when invalid credentials are provided."""
    pass

class APIError(M4300Error):
    """Raised when the API returns an error."""
    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        """Initialize APIError.
        
        Args:
            message: Error message
            status_code: HTTP status code if available
            response: Raw API response if available
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class ValidationError(M4300Error):
    """Raised when input validation fails."""
    pass

class RateLimitError(M4300Error):
    """Raised when rate limit is exceeded."""
    pass

class ConnectionError(M4300Error):
    """Raised when connection to the switch fails."""
    pass

class TimeoutError(M4300Error):
    """Raised when a request times out."""
    pass

class ConfigurationError(M4300Error):
    """Raised when there is a configuration error."""
    pass
