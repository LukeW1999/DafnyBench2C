"""
Abstract interface for Dafny to C converters
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ConversionResult:
    """Result of a conversion operation"""
    success: bool
    c_code: Optional[str] = None
    test_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class IConverter(ABC):
    """Abstract interface for Dafny to C converters"""
    
    @abstractmethod
    def convert(self, dafny_code: str, **kwargs) -> ConversionResult:
        """Convert Dafny code to C code"""
        pass
    
    @abstractmethod
    def convert_file(self, dafny_file: Path, output_dir: Path, **kwargs) -> ConversionResult:
        """Convert a Dafny file to C file"""
        pass
    
    @abstractmethod
    def batch_convert(self, dafny_files: list[Path], output_dir: Path, **kwargs) -> list[ConversionResult]:
        """Convert multiple Dafny files"""
        pass
    
    @abstractmethod
    def get_supported_features(self) -> list[str]:
        """Get list of supported Dafny features"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get converter version"""
        pass 