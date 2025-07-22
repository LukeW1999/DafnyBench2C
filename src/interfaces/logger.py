"""
Abstract interface for logging
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum
from pathlib import Path

class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ILogger(ABC):
    """Abstract interface for logging"""
    
    @abstractmethod
    def log(self, level: LogLevel, message: str, **kwargs):
        """Log a message"""
        pass
    
    @abstractmethod
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs):
        """Log info message"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs):
        """Log error message"""
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        pass
    
    @abstractmethod
    def set_level(self, level: LogLevel):
        """Set log level"""
        pass
    
    @abstractmethod
    def set_output_file(self, file_path: Path):
        """Set output file for logging"""
        pass 