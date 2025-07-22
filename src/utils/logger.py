"""
Logging system implementation
"""

import logging
import sys
from typing import Optional
from pathlib import Path
from src.interfaces import ILogger, LogLevel

class Logger(ILogger):
    """Standard logging implementation"""
    
    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self._file_handler = None
    
    def log(self, level: LogLevel, message: str, **kwargs):
        """Log a message"""
        log_level = getattr(logging, level.value)
        self.logger.log(log_level, message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)
    
    def set_level(self, level: LogLevel):
        """Set log level"""
        self.logger.setLevel(getattr(logging, level.value))
    
    def set_output_file(self, file_path: Path):
        """Set output file for logging"""
        # Remove existing file handler
        if self._file_handler:
            self.logger.removeHandler(self._file_handler)
        
        # Create new file handler
        file_handler = logging.FileHandler(file_path)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self._file_handler = file_handler

# Global logger instances
_loggers = {}

def get_logger(name: str) -> Logger:
    """Get or create a logger instance"""
    if name not in _loggers:
        _loggers[name] = Logger(name)
    return _loggers[name]

def set_log_level(level: LogLevel):
    """Set log level for all loggers"""
    for logger in _loggers.values():
        logger.set_level(level)

def set_log_file(file_path: Path):
    """Set log file for all loggers"""
    for logger in _loggers.values():
        logger.set_output_file(file_path) 