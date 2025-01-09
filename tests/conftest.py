"""Pytest configuration and fixtures for M4300 API helper tests.

This module provides common test configuration and fixtures used across
both unit and integration tests for the M4300 API helpers.

Configuration:
    - SSL warning suppression for cleaner test output
    - Common test data and configurations
    - Integration test markers and skipping

Test Environment:
    - Test switch: 192.168.99.92:8443
    - Admin credentials available
    - Rate limiting: 5 attempts per 5 minutes
"""
import urllib3
import pytest

@pytest.fixture(autouse=True)
def disable_insecure_warnings():
    """Disable InsecureRequestWarning for all tests.
    
    The M4300 switch uses self-signed certificates, so we disable
    SSL verification warnings to keep test output clean.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    yield

# Test switch configuration
TEST_SWITCH = {
    "base_url": "https://192.168.99.92:8443",
    "username": "admin",
    "password": "password123"
}

@pytest.fixture
def switch_config():
    """Provide test switch configuration for integration tests."""
    return TEST_SWITCH.copy()

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
