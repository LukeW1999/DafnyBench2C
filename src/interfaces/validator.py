"""
Abstract interface for code validators
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of a validation operation"""
    is_valid: bool
    score: float
    details: list[str]
    issues: list[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class IValidator(ABC):
    """Abstract interface for code validators"""
    
    @abstractmethod
    def validate_conversion(self, dafny_code: str, c_code: str, **kwargs) -> ValidationResult:
        """Validate Dafny to C conversion"""
        pass
    
    @abstractmethod
    def validate_syntax(self, c_code: str, **kwargs) -> ValidationResult:
        """Validate C code syntax"""
        pass
    
    @abstractmethod
    def validate_semantics(self, dafny_code: str, c_code: str, **kwargs) -> ValidationResult:
        """Validate semantic equivalence"""
        pass
    
    @abstractmethod
    def get_validation_rules(self) -> Dict[str, float]:
        """Get validation rules and their weights"""
        pass 