"""Shared test fixtures and configuration."""

import os
from typing import Generator
from unittest.mock import patch

import pytest
import responses
from requests.models import Response

from m4300api_helpers.client import M4300Client
from m4300api_helpers.config import M4300Config
from tests.fixtures.api_responses import LOGIN_SUCCESS

@pytest.fixture
def mock_env_vars() -> Generator[dict[str, str], None, None]:
    """Mock environment variables for testing.
    
    Yields:
        dict[str, str]: Dictionary of environment variables
    """
    env_vars = {
        "M4300_HOST": "switch.example.com",
        "M4300_USERNAME": "admin",
        "M4300_PASSWORD": "password123",
        "M4300_PORT": "8443",
        "M4300_VERIFY_SSL": "true",
        "M4300_TIMEOUT": "30",
        "M4300_RATE_LIMIT": "10",
        "M4300_TOKEN_REFRESH_MARGIN": "300"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def config() -> M4300Config:
    """Create test configuration.
    
    Returns:
        M4300Config: Test configuration object
    """
    return M4300Config(
        host="switch.example.com",
        username="admin",
        password="password123"
    )

@pytest.fixture
def client(config: M4300Config) -> M4300Client:
    """Create test client.
    
    Args:
        config: Test configuration fixture
        
    Returns:
        M4300Client: Test client object
    """
    return M4300Client(config)

@pytest.fixture
def authenticated_client(client: M4300Client) -> Generator[M4300Client, None, None]:
    """Create authenticated test client.
    
    Args:
        client: Test client fixture
        
    Yields:
        M4300Client: Authenticated test client object
    """
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            f"{client.config.base_url}/login",
            json=LOGIN_SUCCESS,
            status=200
        )
        client.authenticate()
        yield client

@pytest.fixture
def mock_response() -> Response:
    """Create mock response object.
    
    Returns:
        Response: Mock response object
    """
    response = Response()
    response.status_code = 200
    response._content = b'{"resp": {"status": "success"}}'
    return response

def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest.
    
    Args:
        config: Pytest configuration object
    """
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers",
        "live_switch: mark test as requiring live switch"
    )

def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item]
) -> None:
    """Modify test collection.
    
    Args:
        config: Pytest configuration object
        items: List of test items
    """
    # Skip integration tests unless --integration flag is provided
    if not config.getoption("--integration"):
        skip_integration = pytest.mark.skip(reason="need --integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
    
    # Skip live switch tests unless --live-switch flag is provided
    if not config.getoption("--live-switch"):
        skip_live = pytest.mark.skip(reason="need --live-switch option to run")
        for item in items:
            if "live_switch" in item.keywords:
                item.add_marker(skip_live)

def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options.
    
    Args:
        parser: Pytest parser object
    """
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests"
    )
    parser.addoption(
        "--live-switch",
        action="store_true",
        default=False,
        help="run tests against live switch"
    )
