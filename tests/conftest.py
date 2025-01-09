"""Pytest configuration and fixtures for M4300 API helper tests.

This module provides common test configuration and fixtures used across
both unit and integration tests for the M4300 API helpers.

Configuration:
    - SSL warning suppression for cleaner test output
    - Common test data and configurations
    - Integration test markers and skipping

Test Environment:
    Configuration via environment variables:
    - M4300_TEST_HOST: Test switch hostname/IP and port
    - M4300_TEST_USERNAME: Admin username
    - M4300_TEST_PASSWORD: Admin password
    
    Defaults (backward compatibility):
    - Host: 192.168.99.92:8443
    - Username: admin
    - Password: password123
    
    Rate limiting: 5 attempts per 5 minutes
"""
import urllib3
import pytest
import os
from typing import Dict

@pytest.fixture(autouse=True)
def disable_insecure_warnings():
    """Disable InsecureRequestWarning for all tests.
    
    The M4300 switch uses self-signed certificates, so we disable
    SSL verification warnings to keep test output clean.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    yield

def get_test_config() -> Dict[str, str]:
    """Get test configuration from environment variables.
    
    Returns:
        Dictionary with test configuration using environment variables
        or default values for backward compatibility.
        
    Note:
        Prefer environment variables over defaults:
        - M4300_TEST_HOST
        - M4300_TEST_USERNAME
        - M4300_TEST_PASSWORD
    """
    host = os.getenv('M4300_TEST_HOST', '192.168.99.92:8443')
    if not host.startswith('https://'):
        host = f'https://{host}'
        
    return {
        'base_url': host,
        'username': os.getenv('M4300_TEST_USERNAME', 'admin'),
        'password': os.getenv('M4300_TEST_PASSWORD', 'password123')
    }

@pytest.fixture
def switch_config():
    """Provide test switch configuration for integration tests.
    
    Returns:
        Dictionary with test configuration from environment
        variables or default fallback values.
    """
    return get_test_config()

def pytest_configure(config):
    """Add custom markers for test categorization."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as requiring live switch access"
    )

def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless explicitly requested."""
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

def pytest_addoption(parser):
    """Add command line options for test configuration."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests against live switch"
    )
