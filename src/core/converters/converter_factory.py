"""
Factory for creating converter instances
"""

from typing import Optional, Dict, Type
from pathlib import Path

from src.interfaces import IConverter
from src.config import ConverterConfig, ModelConfig
from src.utils.logger import get_logger
from .claude_converter import ClaudeConverter
from .deepseek_converter import DeepSeekConverter

logger = get_logger(__name__)

class ConverterFactory:
    """Factory for creating converter instances"""
    
    _converters: Dict[str, Type[IConverter]] = {
        'claude': ClaudeConverter,
        'deepseek': DeepSeekConverter,
    }
    
    @classmethod
    def register_converter(cls, name: str, converter_class: Type[IConverter]):
        """Register a new converter type"""
        cls._converters[name] = converter_class
        logger.info(f"Registered converter: {name}")
    
    @classmethod
    def create_converter(cls, converter_type: str = 'claude', **kwargs) -> IConverter:
        """Create a converter instance"""
        if converter_type not in cls._converters:
            available = ', '.join(cls._converters.keys())
            raise ValueError(f"Unknown converter type: {converter_type}. Available: {available}")
        
        converter_class = cls._converters[converter_type]
        logger.info(f"Creating converter: {converter_type}")
        return converter_class(**kwargs)
    
    @classmethod
    def get_available_converters(cls) -> list[str]:
        """Get list of available converter types"""
        return list(cls._converters.keys())
    
    @classmethod
    def create_claude_converter(cls, api_key: Optional[str] = None, **kwargs) -> ClaudeConverter:
        """Create a Claude converter with default settings"""
        config = kwargs.get('config', ConverterConfig())
        return ClaudeConverter(api_key=api_key, config=config) 