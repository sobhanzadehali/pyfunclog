import inspect
import logging
import json
from functools import wraps
from typing import Any, Dict, Optional, Callable
from datetime import datetime
from .filters import SensitiveDataDetector, SensitiveDataFilter

class SecureFunctionLogger:
    """
    Main logger class with sensitive data protection
    """
    
    def __init__(self, logger_name: str = "pyfunclog"):
        self.logger = logging.getLogger(logger_name)
        self.sensitive_detector = SensitiveDataDetector()
        
        # Add sensitive data filter if not already present
        if not any(isinstance(f, SensitiveDataFilter) for f in self.logger.filters):
            self.logger.addFilter(SensitiveDataFilter())
            
        self._setup_default_logging()
    
    def _setup_default_logging(self):
        """Setup default logging configuration if none exists"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_function_call(self, func: Callable, args: tuple, kwargs: dict, 
                         locals_dict: Dict[str, Any], return_value: Any = None,
                         exception: Optional[Exception] = None):
        """Log comprehensive function information with sensitive data protection"""
        
        func_name = func.__name__
        module_name = func.__module__
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "function": f"{module_name}.{func_name}",
            "args": self._serialize_args(args, kwargs, func),
            "locals": self._serialize_locals(locals_dict),
            "return_value": self._safe_serialize(return_value),
            "exception": str(exception) if exception else None,
        }
        
        if exception:
            self.logger.error(f"Function execution: {json.dumps(log_data, default=str)}")
        else:
            self.logger.info(f"Function executed: {json.dumps(log_data, default=str)}")
    
    def _serialize_args(self, args: tuple, kwargs: dict, func: Callable) -> Dict[str, Any]:
        """Serialize function arguments with sensitive data protection"""
        try:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            serialized = {}
            for param_name, param_value in bound_args.arguments.items():
                serialized[param_name] = self._safe_serialize(param_value, param_name)
            
            return serialized
        except Exception as e:
            return {"_error": f"Failed to serialize args: {str(e)}"}
    
    def _serialize_locals(self, locals_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize local variables with sensitive data protection"""
        serialized = {}
        for key, value in locals_dict.items():
            if not key.startswith('__') and not key.endswith('__'):
                serialized[key] = self._safe_serialize(value, key)
        return serialized
    
    def _safe_serialize(self, value: Any, key: str = None) -> Any:
        """Secure serialization with sensitive data handling"""
        
        # First check for sensitive data
        if isinstance(value, str):
            masked_value = self.sensitive_detector.mask_sensitive_value(value, key)
            if masked_value != value:
                return masked_value
        
        # Handle basic types
        if value is None:
            return None
        elif isinstance(value, (int, float, bool)):
            return value
        elif isinstance(value, str):
            return value
        elif isinstance(value, (list, tuple)):
            return [self._safe_serialize(item, key) for item in value][:5]  # Limit size
        elif isinstance(value, dict):
            return {str(k): self._safe_serialize(v, str(k)) for k, v in list(value.items())[:5]}
        else:
            # For complex objects, use string representation
            return f"<{type(value).__name__}: {str(value)[:100]}>"

# Global logger instance
_default_logger = SecureFunctionLogger()

def secure_log_function(logger: Optional[SecureFunctionLogger] = None):
    """Main decorator for secure function logging"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_logger = logger or _default_logger
            locals_dict = {}
            return_value = None
            exception = None
            
            try:
                return_value = func(*args, **kwargs)
                
                # Capture local variables from function frame
                frame = inspect.currentframe()
                try:
                    for _ in range(2):  # Navigate to function frame
                        frame = frame.f_back
                        if frame is None:
                            break
                    
                    if frame and frame.f_code == func.__code__:
                        locals_dict = frame.f_locals.copy()
                finally:
                    del frame
                
                local_logger.log_function_call(func, args, kwargs, locals_dict, return_value)
                return return_value
                
            except Exception as e:
                exception = e
                local_logger.log_function_call(func, args, kwargs, locals_dict, return_value, exception)
                raise
        
        return wrapper
    return decorator