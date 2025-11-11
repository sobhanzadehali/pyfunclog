"""
PyFuncLog - Comprehensive function logging with async support and sensitive data protection
"""

from .core import SecureFunctionLogger, secure_log_function, async_secure_log_function
from .decorators import log_all, log_return, log_locals, async_log_all, async_log_return, async_log_locals, universal_log
from .filters import SensitiveDataFilter, SensitiveDataDetector
from .utils import configure_logging, set_log_level
from .async_support import AsyncFunctionLogger, FastAPILoggingSupport

__version__ = "2.0.0"
__all__ = [
    'SecureFunctionLogger',
    'AsyncFunctionLogger',
    'secure_log_function', 
    'async_secure_log_function',
    'log_all',
    'log_return', 
    'log_locals',
    'async_log_all',
    'async_log_return', 
    'async_log_locals',
    'universal_log',
    'SensitiveDataFilter',
    'SensitiveDataDetector',
    'configure_logging',
    'set_log_level',
    'FastAPILoggingSupport'
]