"""Pytest configuration for integration tests."""
import urllib3
import pytest

@pytest.fixture(autouse=True)
def disable_insecure_warnings():
    """Disable InsecureRequestWarning for all tests."""
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    yield
