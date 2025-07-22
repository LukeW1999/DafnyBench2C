"""
Claude-based Dafny to C converter implementation
"""

import os
import re
from typing import Optional, Dict, Any
from pathlib import Path
import anthropic

from src.interfaces import IConverter, ConversionResult
from src.config import get_settings, ConverterConfig, ModelConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ClaudeConverter(IConverter):
    """Claude-based Dafny to C converter"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, config: Optional[ConverterConfig] = None):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.api_key
        self.config = config or ConverterConfig()
        
        if not self.api_key:
            raise ValueError("API key is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Use provided model or default
        if model:
            self.model_config = ModelConfig(
                name=model,
                max_tokens=4096,
                temperature=0.1,
                timeout=60
            )
        else:
            self.model_config = ModelConfig.claude_opus()
        
        logger.info(f"Initialized ClaudeConverter with model: {self.model_config.name}")
    
    def convert(self, dafny_code: str, **kwargs) -> ConversionResult:
        """Convert Dafny code to C code"""
        try:
            logger.info("Starting Dafny to C conversion")
            
            # Step 1: Initial conversion
            initial_result = self._convert_dafny_to_c(dafny_code)
            if not initial_result.success:
                return initial_result
            
            # Step 2: Self-review (if enabled)
            if self.config.enable_self_review:
                logger.info("Performing self-review")
                review_result = self._self_review_and_improve(dafny_code, initial_result.c_code)
                if review_result.success:
                    c_code = review_result.c_code
                else:
                    logger.warning("Self-review failed, using initial conversion")
                    c_code = initial_result.c_code
            else:
                c_code = initial_result.c_code
            
            # Step 3: Code cleaning (if enabled)
            if self.config.enable_code_cleaning:
                logger.info("Cleaning C code")
                c_code = self._clean_c_code(c_code)
            
            # Step 4: Generate test cases (if enabled)
            test_code = None
            if self.config.enable_test_generation:
                logger.info("Generating test cases")
                test_result = self._generate_test_cases(dafny_code, c_code)
                if test_result.success:
                    test_code = test_result.c_code
            
            return ConversionResult(
                success=True,
                c_code=c_code,
                test_code=test_code,
                metadata={
                    'model_used': self.model_config.name,
                    'self_review_enabled': self.config.enable_self_review,
                    'test_generation_enabled': self.config.enable_test_generation
                }
            )
            
        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=str(e)
            )
    
    def convert_file(self, dafny_file: Path, output_dir: Path, **kwargs) -> ConversionResult:
        """Convert a Dafny file to C file"""
        try:
            # Read Dafny file
            with open(dafny_file, 'r', encoding='utf-8') as f:
                dafny_code = f.read()
            
            # Convert
            result = self.convert(dafny_code, **kwargs)
            
            if result.success:
                # Save C file
                os.makedirs(output_dir, exist_ok=True)
                c_file = output_dir / f"{dafny_file.stem}.c"
                with open(c_file, 'w', encoding='utf-8') as f:
                    f.write(result.c_code)
                
                # Save test file
                if result.test_code:
                    test_file = output_dir / f"test_{dafny_file.stem}.c"
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(result.test_code)
                
                logger.info(f"Successfully converted {dafny_file} to {c_file}")
            
            return result
            
        except Exception as e:
            logger.error(f"File conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=str(e)
            )
    
    def batch_convert(self, dafny_files: list[Path], output_dir: Path, **kwargs) -> list[ConversionResult]:
        """Convert multiple Dafny files"""
        results = []
        for dafny_file in dafny_files:
            logger.info(f"Converting {dafny_file}")
            result = self.convert_file(dafny_file, output_dir, **kwargs)
            results.append(result)
        return results
    
    def get_supported_features(self) -> list[str]:
        """Get list of supported Dafny features"""
        return [
            "requires/ensures clauses",
            "loop invariants",
            "array operations",
            "method definitions",
            "predicates",
            "assertions"
        ]
    
    def get_version(self) -> str:
        """Get converter version"""
        return "1.0.0"
    
    def _convert_dafny_to_c(self, dafny_code: str) -> ConversionResult:
        """Initial conversion from Dafny to C"""
        prompt = f"{self.config.conversion_prompt_template}\n\nDafny:\n```dafny\n{dafny_code}\n```\n\nC code:"
        
        try:
            response = self.client.messages.create(
                model=self.model_config.name,
                max_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            c_code = response.content[0].text.strip()
            c_code = self._extract_c_code(c_code)
            
            return ConversionResult(
                success=True,
                c_code=c_code
            )
            
        except Exception as e:
            logger.error(f"Initial conversion error: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=str(e)
            )
    
    def _self_review_and_improve(self, dafny_code: str, c_code: str) -> ConversionResult:
        """Self-review and improve the conversion"""
        prompt = f"{self.config.review_prompt_template}\n\nDafny:\n```dafny\n{dafny_code}\n```\n\nC:\n```c\n{c_code}\n```\n\nImproved C code:"
        
        try:
            response = self.client.messages.create(
                model=self.model_config.name,
                max_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            improved_code = response.content[0].text.strip()
            improved_code = self._extract_c_code(improved_code)
            
            return ConversionResult(
                success=True,
                c_code=improved_code
            )
            
        except Exception as e:
            logger.error(f"Self-review error: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=str(e)
            )
    
    def _generate_test_cases(self, dafny_code: str, c_code: str) -> ConversionResult:
        """Generate test cases for the converted C code"""
        prompt = f"{self.config.test_prompt_template}\n\nDafny:\n```dafny\n{dafny_code}\n```\n\nC:\n```c\n{c_code}\n```\n\nTest file:"
        
        try:
            response = self.client.messages.create(
                model=self.model_config.name,
                max_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            test_code = response.content[0].text.strip()
            test_code = self._extract_c_code(test_code)
            
            return ConversionResult(
                success=True,
                c_code=test_code
            )
            
        except Exception as e:
            logger.error(f"Test generation error: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=str(e)
            )
    
    def _extract_c_code(self, text: str) -> str:
        """Extract C code from markdown code blocks or plain text"""
        # Look for ```c ... ``` blocks
        c_block_pattern = r'```c\s*\n(.*?)\n```'
        match = re.search(c_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Look for ``` ... ``` blocks (without language specifier)
        block_pattern = r'```\s*\n(.*?)\n```'
        match = re.search(block_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # If no code blocks found, return the text as is
        return text
    
    def _clean_c_code(self, c_code: str) -> str:
        """Clean C code by removing test functions and main function"""
        lines = c_code.split('\n')
        cleaned_lines = []
        in_test_function = False
        brace_count = 0
        
        for line in lines:
            # Check if this line starts a test function
            if re.match(r'\s*(void\s+)?test\w*\s*\(', line, re.IGNORECASE):
                in_test_function = True
                brace_count = 0
            
            if in_test_function:
                # Count braces to track function scope
                brace_count += line.count('{') - line.count('}')
                if brace_count <= 0 and line.strip().endswith('}'):
                    in_test_function = False
                    continue
                continue
            
            # Skip main function
            if re.match(r'\s*int\s+main\s*\(', line):
                in_test_function = True
                brace_count = 0
                continue
            
            if not in_test_function:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip() 