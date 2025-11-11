from .core import secure_log_function, async_secure_log_function, SecureFunctionLogger
from .async_support import AsyncFunctionLogger
from functools import wraps
from typing import Optional, Callable
import asyncio

# Synchronous decorators
def log_all(logger: Optional[SecureFunctionLogger] = None):
    """Log everything: arguments, locals, return values, and exceptions (sync)"""
    return secure_log_function(logger)

def log_return(logger: Optional[SecureFunctionLogger] = None):
    """Log only return values with sensitive data protection (sync)"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            return async_log_return(logger)(func)
            
        sync_decorator = secure_log_function(logger)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_logger = logger or SecureFunctionLogger()
            return_value = sync_decorator(func)(*args, **kwargs)
            
            # Additional return-focused logging
            safe_return = local_logger._safe_serialize(return_value)
            local_logger.logger.info(
                f"Function {func.__module__}.{func.__name__} returned: {safe_return}"
            )
            return return_value
        return wrapper
    return decorator

def log_locals(logger: Optional[SecureFunctionLogger] = None):
    """Log only local variables with sensitive data protection (sync)"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            return async_log_locals(logger)(func)
            
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

# Asynchronous decorators
def async_log_all(logger: Optional[AsyncFunctionLogger] = None):
    """Log everything for async functions"""
    return async_secure_log_function(logger)

def async_log_return(logger: Optional[AsyncFunctionLogger] = None):
    """Log only return values for async functions"""
    def decorator(func):
        if not asyncio.iscoroutinefunction(func):
            return log_return(logger)(func)
            
        async_decorator = async_secure_log_function(logger)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            local_logger = logger or AsyncFunctionLogger()
            return_value = await async_decorator(func)(*args, **kwargs)
            
            # Additional return-focused logging
            safe_return = local_logger._safe_serialize(return_value)
            local_logger.logger.info(
                f"Async function {func.__module__}.{func.__name__} returned: {safe_return}"
            )
            return return_value
        return async_wrapper
    return decorator

def async_log_locals(logger: Optional[AsyncFunctionLogger] = None):
    """Log only local variables for async functions"""
    def decorator(func):
        if not asyncio.iscoroutinefunction(func):
            return log_locals(logger)(func)
            
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            local_logger = logger or AsyncFunctionLogger()
            # Note: Local variable capture in async functions is limited
            # We provide a note about this limitation
            
            try:
                return_value = await func(*args, **kwargs)
                
                local_logger.logger.info(
                    f"Async function {func.__module__}.{func.__name__} executed. "
                    f"Note: Local variable capture in async functions has limitations."
                )
                return return_value
                
            except Exception as e:
                local_logger.logger.error(f"Error in async function: {str(e)}")
                raise
        return async_wrapper
    return decorator

# Universal decorator that works for both sync and async
def universal_log(logger: Optional[SecureFunctionLogger] = None):
    """Universal decorator that works for both sync and async functions"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            # Use async decorator for async functions
            return async_secure_log_function(logger)(func)
        else:
            # Use sync decorator for sync functions
            return secure_log_function(logger)(func)
    return decorator