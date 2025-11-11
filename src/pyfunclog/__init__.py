"""
PyFuncLog - Comprehensive function logging with sensitive data protection
"""

from .core import SecureFunctionLogger, secure_log_function
from .decorators import log_all, log_return, log_locals
from .filters import SensitiveDataFilter, SensitiveDataDetector
from .utils import configure_logging, set_log_level

__version__ = "1.0.0"
__all__ = [
    'SecureFunctionLogger',
    'secure_log_function', 
    'log_all',
    'log_return', 
    'log_locals',
    'SensitiveDataFilter',
    'SensitiveDataDetector',
    'configure_logging',
    'set_log_level'
]