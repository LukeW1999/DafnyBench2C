"""
Result types for conversion pipeline
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from .converter import ConversionResult
from .validator import ValidationResult
from .tester import TestResult

@dataclass
class ConversionPipelineResult:
    """Result of the complete conversion pipeline"""
    conversion: ConversionResult
    validation: Optional[ValidationResult] = None
    testing: Optional[TestResult] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {} 