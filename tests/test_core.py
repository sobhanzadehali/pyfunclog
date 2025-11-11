import pytest
import logging
from pyfunclog import secure_log_function, SecureFunctionLogger

class TestSecureFunctionLogger:
    def test_basic_function_logging(self, caplog):
        """Test basic function logging works"""
        
        @secure_log_function()
        def sample_function(x, y):
            total = x + y
            result = total * 2
            return result
        
        with caplog.at_level(logging.INFO):
            result = sample_function(5, 3)
            
        assert result == 16
        log_output = caplog.text
        assert "sample_function" in log_output
        # Check for the variables we expect to see
        assert "total" in log_output or "result" in log_output

    def test_sensitive_data_masking(self, caplog):
        """Test that sensitive data is properly masked"""
        
        @secure_log_function()
        def auth_function(username, password):
            api_key = "sk_live_1234567890abcdef"
            result = f"Authenticated {username}"
            return result
            
        with caplog.at_level(logging.INFO):
            auth_function("john", "secret123")
            
        log_output = caplog.text
        # Check that sensitive data is masked
        assert "secret123" not in log_output
        assert "sk_live_1234567890abcdef" not in log_output
        # Should contain masked versions
        assert "****" in log_output

    def test_function_with_locals(self, caplog):
        """Test function with local variables"""
        
        @secure_log_function()
        def calculate_stats(numbers):
            total = sum(numbers)
            count = len(numbers)
            average = total / count
            maximum = max(numbers)
            return {
                'total': total,
                'average': average,
                'max': maximum
            }
        
        with caplog.at_level(logging.INFO):
            result = calculate_stats([1, 2, 3, 4, 5])
            
        assert result['total'] == 15
        assert result['average'] == 3.0
        log_output = caplog.text
        # Should log the function execution
        assert "calculate_stats" in log_output
        # Should contain some of our data
        assert "total" in log_output or "average" in log_output

    def test_exception_handling(self, caplog):
        """Test function exception logging"""
        
        @secure_log_function()
        def failing_function(x):
            if x < 0:
                raise ValueError("Negative values not allowed")
            return x * 2
        
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                failing_function(-5)
            
        assert "Negative values not allowed" in caplog.text
        assert "failing_function" in caplog.text