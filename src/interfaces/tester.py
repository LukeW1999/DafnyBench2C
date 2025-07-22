"""
Abstract interface for code testers
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TestResult:
    """Result of a test operation"""
    success: bool
    compiles: bool
    runs: bool
    output: Optional[str] = None
    error: Optional[str] = None
    test_results: List[Dict[str, Any]] = None
    csv_file: Optional[Path] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.test_results is None:
            self.test_results = []
        if self.metadata is None:
            self.metadata = {}

class ITester(ABC):
    """Abstract interface for code testers"""
    
    @abstractmethod
    def compile_and_test(self, c_file: Path, **kwargs) -> TestResult:
        """Compile and test a C file"""
        pass
    
    @abstractmethod
    def generate_tests(self, c_code: str, **kwargs) -> str:
        """Generate test cases for C code"""
        pass
    
    @abstractmethod
    def analyze_results(self, test_output: str, **kwargs) -> Dict[str, Any]:
        """Analyze test results"""
        pass
    
    @abstractmethod
    def save_results_csv(self, test_result: TestResult, output_path: Path) -> Path:
        """Save test results to CSV"""
        pass 