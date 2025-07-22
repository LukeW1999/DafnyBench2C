"""
Factory for creating service instances
"""

from typing import Optional, Dict, Any
from src.interfaces import IConverter, IValidator, ITester
from src.config import ConverterConfig, TestConfig
from src.utils.logger import get_logger
from src.core.converters import ConverterFactory
from src.core.validators import ValidatorFactory
from src.core.testers import TesterFactory
from .conversion_service import ConversionService

logger = get_logger(__name__)

class ServiceFactory:
    """Factory for creating service instances"""
    
    @classmethod
    def create_conversion_service(cls,
                                 converter_type: str = 'claude',
                                 validator_type: str = 'heuristic',
                                 tester_type: str = 'gcc',
                                 converter_config: Optional[ConverterConfig] = None,
                                 test_config: Optional[TestConfig] = None,
                                 save_results: bool = True,
                                 **kwargs) -> ConversionService:
        """Create a conversion service with specified components"""
        
        logger.info(f"Creating conversion service with components: {converter_type}, {validator_type}, {tester_type}")
        
        # Create components
        converter = ConverterFactory.create_converter(converter_type, **kwargs)
        validator = ValidatorFactory.create_validator(validator_type, config=test_config)
        tester = TesterFactory.create_tester(tester_type)
        
        # Create service
        service = ConversionService(
            converter=converter,
            validator=validator,
            tester=tester,
            converter_config=converter_config,
            test_config=test_config,
            save_results=save_results
        )
        
        logger.info("Conversion service created successfully")
        return service
    
    @classmethod
    def create_default_service(cls, **kwargs) -> ConversionService:
        """Create a conversion service with default settings"""
        return cls.create_conversion_service(**kwargs) 