"""Configuration management for M4300 API Helper library."""

from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

from .exceptions import ConfigurationError

# Load environment variables from .env file
load_dotenv()

@dataclass
class M4300Config:
    """Configuration for M4300 API Helper library.
    
    Attributes:
        host: Switch hostname or IP address
        username: Username for authentication
        password: Password for authentication
        port: HTTPS port number (default: 8443)
        verify_ssl: Whether to verify SSL certificates (default: True)
        timeout: Request timeout in seconds (default: 30)
        rate_limit: Maximum requests per second (default: 10)
        token_refresh_margin: Seconds before token expiry to refresh (default: 300)
    """
    host: str
    username: str
    password: str
    port: int = 8443
    verify_ssl: bool = True
    timeout: int = 30
    rate_limit: int = 10
    token_refresh_margin: int = 300

    @classmethod
    def from_env(cls) -> 'M4300Config':
        """Create configuration from environment variables.
        
        Environment Variables:
            M4300_HOST: Switch hostname or IP address
            M4300_USERNAME: Username for authentication
            M4300_PASSWORD: Password for authentication
            M4300_PORT: HTTPS port number (optional)
            M4300_VERIFY_SSL: Whether to verify SSL certificates (optional)
            M4300_TIMEOUT: Request timeout in seconds (optional)
            M4300_RATE_LIMIT: Maximum requests per second (optional)
            M4300_TOKEN_REFRESH_MARGIN: Seconds before token expiry to refresh (optional)
        
        Returns:
            M4300Config: Configuration object

        Raises:
            ConfigurationError: If required environment variables are missing
        """
        required_vars = {
            'M4300_HOST': 'host',
            'M4300_USERNAME': 'username',
            'M4300_PASSWORD': 'password'
        }
        
        # Check required variables
        missing = [env for env in required_vars if not os.getenv(env)]
        if missing:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        
        # Get optional variables with defaults
        optional_vars = {
            'M4300_PORT': ('port', int, 8443),
            'M4300_VERIFY_SSL': ('verify_ssl', lambda x: x.lower() == 'true', True),
            'M4300_TIMEOUT': ('timeout', int, 30),
            'M4300_RATE_LIMIT': ('rate_limit', int, 10),
            'M4300_TOKEN_REFRESH_MARGIN': ('token_refresh_margin', int, 300)
        }
        
        # Build config dict
        config = {
            attr: os.getenv(env)
            for env, attr in required_vars.items()
        }
        
        # Add optional variables
        for env, (attr, type_func, default) in optional_vars.items():
            value = os.getenv(env)
            config[attr] = type_func(value) if value is not None else default
            
        return cls(**config)

    @property
    def base_url(self) -> str:
        """Get the base URL for API requests.
        
        Returns:
            str: Base URL including protocol, host and port
        """
        return f"https://{self.host}:{self.port}/api/v1"
