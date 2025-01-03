"""Base client for M4300 API Helper library."""

import time
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import M4300Config
from .exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    InvalidCredentialsError,
    RateLimitError,
    TimeoutError,
    TokenExpiredError,
)

class M4300Client:
    """Base client for M4300 API Helper library.
    
    This class handles:
    - Authentication and token management
    - Rate limiting
    - HTTP request handling
    - Response validation
    
    Attributes:
        config: Configuration object
        session: Requests session for connection pooling
        _auth_token: Current authentication token
        _token_expires: Token expiration timestamp
        _last_request_time: Time of last API request for rate limiting
    """
    
    def __init__(self, config: M4300Config):
        """Initialize client.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.session = self._create_session()
        self._auth_token: Optional[str] = None
        self._token_expires: Optional[float] = None
        self._last_request_time: float = 0
        
    def _create_session(self) -> requests.Session:
        """Create and configure requests session.
        
        Returns:
            requests.Session: Configured session
        """
        session = requests.Session()
        
        # Configure retries
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        
        # Mount adapter with retry configuration
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        
        # Configure verification
        session.verify = self.config.verify_ssl
        
        return session
    
    def _wait_for_rate_limit(self) -> None:
        """Wait if needed to comply with rate limiting."""
        if self._last_request_time == 0:
            self._last_request_time = time.time()
            return
            
        # Calculate minimum time between requests
        min_interval = 1.0 / self.config.rate_limit
        
        # Calculate time to wait
        elapsed = time.time() - self._last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
            
        self._last_request_time = time.time()
        
    def _check_token_expiry(self) -> None:
        """Check if token needs refresh.
        
        Raises:
            TokenExpiredError: If token has expired
        """
        if not self._auth_token or not self._token_expires:
            return
            
        if time.time() >= self._token_expires - self.config.token_refresh_margin:
            self._auth_token = None
            self._token_expires = None
            raise TokenExpiredError("Authentication token has expired")
            
    def _handle_auth_response(self, response: Dict[str, Any]) -> None:
        """Handle authentication response.
        
        Args:
            response: Authentication response from API
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            token_data = response["login"]
            self._auth_token = token_data["token"]
            self._token_expires = time.time() + token_data["expires"]
        except (KeyError, TypeError) as e:
            raise AuthenticationError(f"Invalid authentication response: {e}")
            
    def authenticate(self) -> None:
        """Authenticate with the API.
        
        Raises:
            InvalidCredentialsError: If credentials are invalid
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            TimeoutError: If request times out
        """
        try:
            response = self.session.post(
                f"{self.config.base_url}/login",
                json={
                    "login": {
                        "username": self.config.username,
                        "password": self.config.password
                    }
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 401:
                raise InvalidCredentialsError("Invalid username or password")
                
            response.raise_for_status()
            self._handle_auth_response(response.json())
            
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Authentication request timed out: {e}")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to switch: {e}")
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Authentication failed: {e}")
            
    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Make an API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json: JSON body
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            TokenExpiredError: If token has expired
            APIError: If API returns an error
            ConnectionError: If connection fails
            TimeoutError: If request times out
            RateLimitError: If rate limit is exceeded
        """
        # Check authentication
        if not self._auth_token:
            self.authenticate()
            
        self._check_token_expiry()
        
        # Apply rate limiting
        self._wait_for_rate_limit()
        
        # Prepare request
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self._auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json,
                headers=headers,
                timeout=self.config.timeout,
                **kwargs
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")
                
            # Handle authentication errors
            if response.status_code == 401:
                self._auth_token = None
                self._token_expires = None
                raise TokenExpiredError("Authentication token expired")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request timed out: {e}")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to switch: {e}")
        except requests.exceptions.HTTPError as e:
            raise APIError(
                str(e),
                status_code=e.response.status_code,
                response=e.response.json() if e.response.content else None
            )
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")
            
    def get(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make GET request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments passed to request()
            
        Returns:
            Dict[str, Any]: API response
        """
        return self.request("GET", endpoint, **kwargs)
        
    def post(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make POST request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments passed to request()
            
        Returns:
            Dict[str, Any]: API response
        """
        return self.request("POST", endpoint, **kwargs)
        
    def delete(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make DELETE request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments passed to request()
            
        Returns:
            Dict[str, Any]: API response
        """
        return self.request("DELETE", endpoint, **kwargs)
