"""
Logging configuration for Orion Phi-4 system
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import colorlog


class OrionLogger:
    """Advanced logging system for Orion Phi-4"""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.log_dir = Path("logs")
            self.log_dir.mkdir(exist_ok=True)
            self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup root logger with color support"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Console handler with colors
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(
            self.log_dir / f"orion_{timestamp}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name"""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]


# Global logger instance
_orion_logger = OrionLogger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return _orion_logger.get_logger(name)
