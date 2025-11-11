import logging
import asyncio
from .filters import SensitiveDataFilter
from .async_support import AsyncFunctionLogger

def configure_logging(level: int = logging.INFO, 
                     format_string: str = None,
                     filename: str = None,
                     enable_sensitive_filter: bool = True,
                     async_logger: bool = False):
    """
    Configure logging for the package with async support
    """
    logger_name = "pyfunclog.async" if async_logger else "pyfunclog"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Create handler
    if filename:
        handler = logging.FileHandler(filename)
    else:
        handler = logging.StreamHandler()
    
    handler.setFormatter(formatter)
    
    # Add sensitive data filter
    if enable_sensitive_filter:
        handler.addFilter(SensitiveDataFilter())
    
    logger.addHandler(handler)

def set_log_level(level: int, async_logger: bool = False):
    """Set log level for pyfunclog"""
    logger_name = "pyfunclog.async" if async_logger else "pyfunclog"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

async def configure_async_logging(level: int = logging.INFO, 
                                 format_string: str = None,
                                 filename: str = None):
    """Async-friendly logging configuration"""
    configure_logging(level, format_string, filename, async_logger=True)