import logging
from .filters import SensitiveDataFilter

def configure_logging(level: int = logging.INFO, 
                     format_string: str = None,
                     filename: str = None,
                     enable_sensitive_filter: bool = True):
    """
    Configure logging for the package[citation:6]
    """
    logger = logging.getLogger("pyfunclog")
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

def set_log_level(level: int):
    """Set log level for pyfunclog"""
    logger = logging.getLogger("pyfunclog")
    logger.setLevel(level)