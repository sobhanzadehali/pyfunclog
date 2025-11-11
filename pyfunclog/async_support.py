"""
Specialized support for asynchronous functions and frameworks
"""
import inspect
import asyncio
import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps
from .core import SecureFunctionLogger
from .filters import SensitiveDataDetector

class AsyncFunctionLogger(SecureFunctionLogger):
    """
    Enhanced logger with better async support
    """
    
    def __init__(self, logger_name: str = "pyfunclog.async"):
        super().__init__(logger_name)
    
    async def log_async_function(self, func: Callable, args: tuple, kwargs: dict, 
                                return_value: Any = None, exception: Optional[Exception] = None):
        """Specialized logging for async functions"""
        # For async functions, we capture locals differently
        locals_dict = await self._capture_async_locals(func, args, kwargs)
        
        self.log_function_call(
            func, args, kwargs, locals_dict, return_value, exception, is_async=True
        )
    
    async def _capture_async_locals(self, func: Callable, args: tuple, kwargs: dict) -> Dict[str, Any]:
        """Capture local variables from async function execution"""
        # This is a simplified approach - in practice, capturing locals from 
        # async functions is more complex and may require different strategies
        return {
            "_note": "Async locals capture requires special handling",
            "function": func.__name__,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys())
        }
    
    def wrap_async_function(self, func: Callable):
        """Wrapper for async functions that preserves type hints and metadata"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return_value = None
            exception = None
            
            try:
                # Execute the async function
                return_value = await func(*args, **kwargs)
                await self.log_async_function(func, args, kwargs, return_value)
                return return_value
            except Exception as e:
                exception = e
                await self.log_async_function(func, args, kwargs, return_value, exception)
                raise
        
        return async_wrapper

# FastAPI/Starlette specific support
try:
    from starlette.requests import Request
    from starlette.responses import Response
    from fastapi import FastAPI, Depends
    
    class FastAPILoggingSupport:
        """Specialized support for FastAPI framework"""
        
        def __init__(self, logger: Optional[AsyncFunctionLogger] = None):
            self.logger = logger or AsyncFunctionLogger()
        
        def log_request(self, request: Request):
            """Log FastAPI request details"""
            log_data = {
                "method": request.method,
                "url": str(request.url),
                "headers": self._safe_headers(dict(request.headers)),
                "client": f"{request.client.host}:{request.client.port}" if request.client else None
            }
            
            self.logger.logger.info(f"FastAPI Request: {log_data}")
        
        def log_response(self, request: Request, response: Response, duration_ms: float):
            """Log FastAPI response details"""
            log_data = {
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "headers": self._safe_headers(dict(response.headers))
            }
            
            self.logger.logger.info(f"FastAPI Response: {log_data}")
        
        def _safe_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
            """Sanitize headers for logging"""
            sensitive_headers = {'authorization', 'cookie', 'set-cookie', 'proxy-authorization'}
            return {
                k: '***' if k.lower() in sensitive_headers else v
                for k, v in headers.items()
            }
        
        def middleware(self, app: FastAPI):
            """FastAPI middleware for automatic request/response logging"""
            @app.middleware("http")
            async def logging_middleware(request: Request, call_next):
                import time
                start_time = time.time()
                
                # Log request
                self.log_request(request)
                
                # Process request
                response = await call_next(request)
                
                # Calculate duration and log response
                duration_ms = (time.time() - start_time) * 1000
                self.log_response(request, response, duration_ms)
                
                return response
            
            return app

except ImportError:
    # FastAPI/Starlette not available
    class FastAPILoggingSupport:
        def __init__(self, *args, **kwargs):
            raise ImportError("FastAPI/Starlette not installed. Install with: pip install pyfunclog[fastapi]")