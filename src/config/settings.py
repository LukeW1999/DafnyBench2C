"""
Settings management using Pydantic for type safety
"""

from typing import Optional, Dict, Any
from pathlib import Path
import os
from dataclasses import dataclass, field

@dataclass
class Settings:
    """Global settings for the application"""
    
    # API Configuration
    api_key: Optional[str] = None
    model: str = "claude-3-opus-20240229"
    max_tokens: int = 4096
    temperature: float = 0.1
    
    # File Paths
    output_dir: str = "converted_c"
    test_dir: str = "test_cases"
    results_dir: str = "results"
    
    # Conversion Settings
    enable_self_review: bool = True
    enable_validation: bool = True
    enable_test_generation: bool = True
    enable_csv_output: bool = True
    
    # Timeout Settings
    compilation_timeout: int = 60  # 编译超时增加到60秒
    execution_timeout: int = 100   # 执行超时增加到100秒
    api_timeout: int = 120         # API超时增加到2分钟
    
    # Validation Settings
    correctness_threshold: float = 0.8
    uncertain_threshold: float = 0.5
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    def __post_init__(self):
        """Set default API key from environment if not provided"""
        if not self.api_key:
            self.api_key = os.getenv("CLAUDE_API_KEY")
    
    def get_output_path(self, filename: str) -> Path:
        """Get full output path for a file"""
        return Path(self.output_dir) / filename
    
    def get_test_path(self, filename: str) -> Path:
        """Get full test path for a file"""
        return Path(self.test_dir) / filename
    
    def get_results_path(self, filename: str) -> Path:
        """Get full results path for a file"""
        return Path(self.results_dir) / filename

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get global settings instance (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def update_settings(**kwargs) -> Settings:
    """Update global settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    
    for key, value in kwargs.items():
        if hasattr(_settings, key):
            setattr(_settings, key, value)
    
    return _settings 