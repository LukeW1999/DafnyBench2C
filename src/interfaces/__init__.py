"""
Abstract interfaces for the conversion system
"""

from .converter import IConverter, ConversionResult
from .validator import IValidator, ValidationResult
from .tester import ITester, TestResult
from .logger import ILogger, LogLevel
from .results import ConversionPipelineResult

__all__ = [
    'IConverter', 'ConversionResult',
    'IValidator', 'ValidationResult', 
    'ITester', 'TestResult',
    'ILogger', 'LogLevel', 'ConversionPipelineResult'
] 