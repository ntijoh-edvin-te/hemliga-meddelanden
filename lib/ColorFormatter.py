import logging
from colorama import Fore, Style

class ColorFormatter(logging.Formatter):
    """
    Custom formatter.
    Logs messages in different colors based on their levels.
    """
    
    COLORS = {
        'INFO': '\033[92m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, self.RESET)}%(levelname)s: %(message)s{self.RESET}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)