from .core import secure_log_function, SecureFunctionLogger
from functools import wraps
from typing import Optional

def log_all(logger: Optional[SecureFunctionLogger] = None):
    """Log everything: arguments, locals, return values, and exceptions"""
    return secure_log_function(logger)

def log_return(logger: Optional[SecureFunctionLogger] = None):
    """Log only return values with sensitive data protection"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_logger = logger or SecureFunctionLogger()
            return_value = func(*args, **kwargs)
            
            # Safe serialization of return value
            safe_return = local_logger._safe_serialize(return_value)
            
            local_logger.logger.info(
                f"Function {func.__module__}.{func.__name__} returned: {safe_return}"
            )
            return return_value
        return wrapper
    return decorator

def log_locals(logger: Optional[SecureFunctionLogger] = None):
    """Log only local variables with sensitive data protection"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_logger = logger or SecureFunctionLogger()
            locals_dict = {}
            
            try:
                return_value = func(*args, **kwargs)
                
                # Capture locals after function execution
                import inspect
                frame = inspect.currentframe()
                try:
                    for _ in range(2):
                        frame = frame.f_back
                        if frame is None:
                            break
                    
                    if frame and frame.f_code == func.__code__:
                        locals_dict = frame.f_locals.copy()
                finally:
                    del frame
                
                # Safe serialization of locals
                safe_locals = local_logger._serialize_locals(locals_dict)
                
                local_logger.logger.info(
                    f"Function {func.__module__}.{func.__name__} locals: {safe_locals}"
                )
                return return_value
                
            except Exception as e:
                local_logger.logger.error(f"Error capturing locals: {str(e)}")
                raise
        return wrapper
    return decorator