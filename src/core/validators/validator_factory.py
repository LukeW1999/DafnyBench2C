"""
Factory for creating validator instances
"""

from typing import Dict, Type, Optional
from src.interfaces import IValidator
from src.config import TestConfig
from src.utils.logger import get_logger
from .heuristic_validator import HeuristicValidator

logger = get_logger(__name__)

class ValidatorFactory:
    """Factory for creating validator instances"""
    
    _validators: Dict[str, Type[IValidator]] = {
        'heuristic': HeuristicValidator,
    }
    
    @classmethod
    def register_validator(cls, name: str, validator_class: Type[IValidator]):
        """Register a new validator type"""
        cls._validators[name] = validator_class
        logger.info(f"Registered validator: {name}")
    
    @classmethod
    def create_validator(cls, validator_type: str = 'heuristic', **kwargs) -> IValidator:
        """Create a validator instance"""
        if validator_type not in cls._validators:
            available = ', '.join(cls._validators.keys())
            raise ValueError(f"Unknown validator type: {validator_type}. Available: {available}")
        
        validator_class = cls._validators[validator_type]
        logger.info(f"Creating validator: {validator_type}")
        return validator_class(**kwargs)
    
    @classmethod
    def get_available_validators(cls) -> list[str]:
        """Get list of available validator types"""
        return list(cls._validators.keys())
    
    @classmethod
    def create_heuristic_validator(cls, config: Optional[TestConfig] = None) -> HeuristicValidator:
        """Create a heuristic validator with default settings"""
        return HeuristicValidator(config=config) 