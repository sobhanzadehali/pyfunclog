import pytest
import asyncio
import logging
from pyfunclog import async_secure_log_function, AsyncFunctionLogger, universal_log

pytestmark = pytest.mark.asyncio

class TestAsyncFunctions:
    async def test_async_function_logging(self, caplog):
        """Test that async functions are properly logged"""
        logger = AsyncFunctionLogger()
        
        @async_secure_log_function(logger)
        async def async_add(x, y):
            result = x + y
            await asyncio.sleep(0.01)
            intermediate = result * 2
            return intermediate
        
        with caplog.at_level(logging.INFO):
            result = await async_add(5, 3)
            
        assert result == 16
        assert "async_add" in caplog.text
        assert "async" in caplog.text.lower()

    async def test_async_function_with_sensitive_data(self, caplog):
        """Test async function with sensitive data masking"""
        
        @async_secure_log_function()
        async def async_auth(username, password):
            api_key = "sk_live_1234567890abcdef"
            token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            await asyncio.sleep(0.01)
            return {"status": "success", "user": username}
        
        with caplog.at_level(logging.INFO):
            await async_auth("john", "secret123")
            
        # Verify sensitive data is masked
        log_output = caplog.text
        assert "secret123" not in log_output
        assert "sk_live" not in log_output
        assert "****" in log_output

    def test_universal_decorator_sync(self, caplog):
        """Test universal decorator with sync function"""
        
        @universal_log()
        def sync_function(x):
            return x * 2
        
        with caplog.at_level(logging.INFO):
            result = sync_function(5)
            
        assert result == 10
        assert "sync_function" in caplog.text

    async def test_universal_decorator_async(self, caplog):
        """Test universal decorator with async function"""
        
        @universal_log()
        async def async_function(x):
            await asyncio.sleep(0.01)
            return x * 2
        
        with caplog.at_level(logging.INFO):
            result = await async_function(5)
            
        assert result == 10
        assert "async_function" in caplog.text

    async def test_async_exception_handling(self, caplog):
        """Test async function exception logging"""
        
        @async_secure_log_function()
        async def async_fail():
            await asyncio.sleep(0.01)
            raise ValueError("Async error occurred")
        
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                await async_fail()
            
        assert "Async error occurred" in caplog.text
        assert "async_fail" in caplog.text