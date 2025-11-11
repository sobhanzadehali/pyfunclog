import re
import logging
from typing import Any, Dict, List

class SensitiveDataDetector:
    """
    Detect and mask sensitive data in log messages
    """
    
    def __init__(self):
        self.sensitive_keywords = {
            'password', 'passwd', 'pwd', 'secret', 'token', 'key', 
            'api_key', 'api_secret', 'jwt', 'bearer', 'auth',
            'credential', 'private_key', 'secret_key', 'access_key',
            'session', 'cookie', 'authorization', 'ssn', 'social_security'
        }
        
    def is_sensitive_key(self, key: str) -> bool:
        """Check if a variable name indicates sensitive data"""
        if not key or not isinstance(key, str):
            return False
            
        key_lower = key.lower()
        return any(sensitive_word in key_lower for sensitive_word in self.sensitive_keywords)

    def mask_sensitive_value(self, value: Any, key: str = None) -> Any:
        """Mask sensitive values based on key name or value pattern"""
        if value is None:
            return None
            
        str_value = str(value)
        
        # Key-based detection
        if key and self.is_sensitive_key(key):
            return self._apply_masking(str_value)
            
        # Value-based pattern detection
        if self._matches_sensitive_pattern(str_value):
            return self._apply_masking(str_value)
            
        return value

    def _apply_masking(self, value: str) -> str:
        """Apply appropriate masking based on value length"""
        if len(value) <= 4:
            return "****"
        elif len(value) <= 8:
            return value[:2] + "*" * (len(value) - 2)
        else:
            return value[:4] + "*" * (len(value) - 8) + value[-4:]

    def _matches_sensitive_pattern(self, value: str) -> bool:
        """Detect sensitive data patterns in values"""
        patterns = [
            r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$',  # JWT
            r'^[a-f0-9]{20,}$',  # Long hex strings
            r'^bearer\s+[a-z0-9]',  # Bearer tokens
            r'^[A-Za-z0-9+/]{40,}={0,2}$',  # Common secret patterns
        ]
        
        return any(re.match(pattern, value, re.IGNORECASE) for pattern in patterns)

class SensitiveDataFilter(logging.Filter):
    """
    Logging filter to mask sensitive data in log records
    """
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.detector = SensitiveDataDetector()

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and mask sensitive data in log records"""
        try:
            # Mask sensitive data in the message
            if hasattr(record, 'msg') and record.msg:
                record.msg = self._process_message(record.msg)
            
            # Mask sensitive data in arguments
            if hasattr(record, 'args') and record.args:
                record.args = self._process_args(record.args)
                
        except Exception:
            # If masking fails, still allow the log through
            pass
            
        return True

    def _process_message(self, message: Any) -> Any:
        """Process message for sensitive data"""
        if isinstance(message, str):
            return self.detector.mask_sensitive_value(message)
        elif isinstance(message, dict):
            return self._process_dict(message)
        return message

    def _process_args(self, args: Any) -> Any:
        """Process arguments for sensitive data"""
        if isinstance(args, tuple):
            return tuple(self._process_message(arg) for arg in args)
        elif isinstance(args, dict):
            return self._process_dict(args)
        return args

    def _process_dict(self, data: Dict) -> Dict:
        """Process dictionary for sensitive data"""
        processed = {}
        for key, value in data.items():
            processed[key] = self.detector.mask_sensitive_value(value, str(key))
        return processed