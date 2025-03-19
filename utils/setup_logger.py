import logging
import sys
from colorama import init

def setup_logger(formatter_class=None):
    """
    Set up logger with custom formatting.
    
    Args:
        formatter_class: Class to use for formatting (default: logging.Formatter)
    """
    init()
    logger = logging.getLogger("steganography")
    logger.setLevel(logging.INFO)
    
    if logger.hasHandlers():
        logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    formatter = formatter_class() if formatter_class else logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger