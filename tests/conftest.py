"""
Pytest configuration for async tests
"""
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Enable asyncio for all async tests
def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")