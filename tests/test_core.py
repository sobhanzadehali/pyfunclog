import pytest
import logging
from pyfunclog import secure_log_function, SecureFunctionLogger

class TestSecureFunctionLogger:
    def test_basic_function_logging(self, caplog):
        """Test basic function logging works"""
        logger = SecureFunctionLogger()
        
        @secure_log_function(logger)
        def sample_function(x, y):
            result = x + y
            return result
        
        with caplog.at_level(logging.INFO):
            sample_function(5, 3)
            
        assert "sample_function" in caplog.text
        assert "result" in caplog.text

    def test_sensitive_data_masking(self, caplog):
        """Test that sensitive data is properly masked"""
        logger = SecureFunctionLogger()
        
        @secure_log_function(logger)
        def auth_function(username, password):
            api_key = "sk_live_1234567890abcdef"
            return True
            
        with caplog.at_level(logging.INFO):
            auth_function("john", "secret123")
            
        # Check that sensitive data is masked
        assert "secret123" not in caplog.text
        assert "sk_live" not in caplog.text
        assert "****" in caplog.text

if __name__ == "__main__":
    pytest.main()