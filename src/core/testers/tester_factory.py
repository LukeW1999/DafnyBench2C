"""
Factory for creating tester instances
"""

from typing import Dict, Type, Optional
from src.interfaces import ITester
from src.utils.logger import get_logger
from .gcc_tester import GCCTester

logger = get_logger(__name__)

class TesterFactory:
    """Factory for creating tester instances"""
    
    _testers: Dict[str, Type[ITester]] = {
        'gcc': GCCTester,
    }
    
    @classmethod
    def register_tester(cls, name: str, tester_class: Type[ITester]):
        """Register a new tester type"""
        cls._testers[name] = tester_class
        logger.info(f"Registered tester: {name}")
    
    @classmethod
    def create_tester(cls, tester_type: str = 'gcc', **kwargs) -> ITester:
        """Create a tester instance"""
        if tester_type not in cls._testers:
            available = ', '.join(cls._testers.keys())
            raise ValueError(f"Unknown tester type: {tester_type}. Available: {available}")
        
        tester_class = cls._testers[tester_type]
        logger.info(f"Creating tester: {tester_type}")
        return tester_class(**kwargs)
    
    @classmethod
    def get_available_testers(cls) -> list[str]:
        """Get list of available tester types"""
        return list(cls._testers.keys())
    
    @classmethod
    def create_gcc_tester(cls, timeout: Optional[int] = None) -> GCCTester:
        """Create a GCC tester with default settings"""
        return GCCTester(timeout=timeout) 