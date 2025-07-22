"""
DeepSeek converter implementation using OpenAI-compatible API
"""

import openai
from typing import Optional, Dict, Any
from pathlib import Path
from src.interfaces import IConverter, ConversionResult
from src.config import ModelConfig, ConverterConfig, get_settings
from src.utils.logger import get_logger
from openai import OpenAI

logger = get_logger(__name__)

class DeepSeekConverter(IConverter):
    """DeepSeek converter for Dafny to C conversion"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, config: Optional[ConverterConfig] = None):
        """Initialize DeepSeek converter"""
        self.config = config or ConverterConfig()
        
        # Get API key from settings if not provided
        if not api_key:
            from src.config import get_settings
            settings = get_settings()
            api_key = settings.api_key
        
        if not api_key:
            raise ValueError("API key is required for DeepSeek converter")
        
        # Initialize OpenAI client for DeepSeek
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            timeout=120
        )
        
        # Use provided model or default
        if model:
            self.model_config = ModelConfig(
                name=model,
                api_base="https://api.deepseek.com",
                api_key=api_key,
                model=model,
                timeout=120
            )
        else:
            self.model_config = ModelConfig.deepseek_chat(api_key)
        
        logger.info(f"Initialized DeepSeekConverter with model: {self.model_config.name}")
    
    def convert(self, dafny_code: str, **kwargs) -> ConversionResult:
        """Convert Dafny code to C code"""
        try:
            logger.info("Starting Dafny to C conversion with DeepSeek")
            
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
    
    def _convert_dafny_to_c(self, dafny_code: str) -> ConversionResult:
        """Convert Dafny code to C with ACSL annotations"""
        try:
            prompt = f"""Convert the following Dafny code to C with ACSL annotations. 

IMPORTANT RULES:
1. ONLY convert existing `ensures` and `requires` clauses to ACSL annotations
2. DO NOT add any new `ensures` or `requires` clauses that don't exist in the original Dafny code
3. DO NOT add any additional validation or error checking beyond what's in the original code
4. Keep the function behavior exactly as specified in the original Dafny code
5. Return ONLY the C code without any explanations

Dafny code:
{dafny_code}

C code with ACSL annotations:"""

            response = self.client.chat.completions.create(
                model=self.model_config.name,
                messages=[
                    {"role": "system", "content": "You are an expert in formal verification and code conversion. Convert Dafny code to C with ACSL annotations, but ONLY convert existing ensures/requires clauses. Do not add new ones."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature
            )
            
            c_code = response.choices[0].message.content.strip()
            
            # Clean up the response
            if c_code.startswith("```c"):
                c_code = c_code[4:]
            if c_code.endswith("```"):
                c_code = c_code[:-3]
            c_code = c_code.strip()
            
            return ConversionResult(
                success=True,
                c_code=c_code
            )
            
        except Exception as e:
            logger.error(f"Initial conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=f"Initial conversion failed: {str(e)}"
            )
    
    def _self_review_and_improve(self, dafny_code: str, c_code: str) -> ConversionResult:
        """Self-review and improve the conversion"""
        try:
            prompt = f"""Review and improve the following Dafny to C conversion. Focus on:
1. Correctness of ACSL annotations
2. Proper array handling with length parameters
3. Loop invariant preservation
4. Function signature accuracy

Original Dafny code:
{dafny_code}

Current C code:
{c_code}

Return ONLY the improved C code:"""

            response = self.client.chat.completions.create(
                model=self.model_config.name,
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer specializing in formal verification."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature
            )
            
            improved_code = response.choices[0].message.content.strip()
            
            # Clean up the response
            if improved_code.startswith("```c"):
                improved_code = improved_code[4:]
            if improved_code.endswith("```"):
                improved_code = improved_code[:-3]
            improved_code = improved_code.strip()
            
            return ConversionResult(
                success=True,
                c_code=improved_code
            )
            
        except Exception as e:
            logger.error(f"Self-review failed: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=f"Self-review failed: {str(e)}"
            )
    
    def _generate_test_cases(self, dafny_code: str, c_code: str) -> ConversionResult:
        """Generate test cases for the converted C code"""
        try:
            prompt = f"""Generate a complete C test file for the following C function. 

IMPORTANT RULES:
1. Copy the original C function definition INTO the test file (don't use #include)
2. Create a main() function that tests the original function
3. Test ONLY the functionality that exists in the original Dafny code
4. DO NOT add tests for functionality that doesn't exist in the original
5. Keep tests simple and focused on the original behavior
6. Return ONLY the complete C test file without explanations

Original C function:
{c_code}

Complete C test file with main():"""

            response = self.client.chat.completions.create(
                model=self.model_config.name,
                messages=[
                    {"role": "system", "content": "You are an expert in C testing. Generate test files that copy the original function and test only existing functionality."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature
            )
            
            test_code = response.choices[0].message.content.strip()
            
            # Clean up the response
            if test_code.startswith("```c"):
                test_code = test_code[4:]
            if test_code.endswith("```"):
                test_code = test_code[:-3]
            test_code = test_code.strip()
            
            return ConversionResult(
                success=True,
                c_code=test_code
            )
            
        except Exception as e:
            logger.error(f"Test generation failed: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=f"Test generation failed: {str(e)}"
            )
    
    def _clean_c_code(self, c_code: str) -> str:
        """Clean and format C code"""
        # Remove markdown code blocks
        if c_code.startswith("```c"):
            c_code = c_code[4:]
        if c_code.endswith("```"):
            c_code = c_code[:-3]
        
        # Remove explanatory text before and after code
        lines = c_code.split('\n')
        cleaned_lines = []
        in_code_block = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and explanatory text
            if not line:
                continue
                
            # Skip lines that are clearly explanatory text
            if any(skip in line.lower() for skip in [
                "here's the", "improved c code", "key improvements:", 
                "additional", "safety checks", "more precise",
                "strengthened", "simplified", "made", "added"
            ]):
                continue
                
            # Skip numbered lists
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                continue
                
            # If we find a C comment or function, we're in the code block
            if line.startswith('/*@') or line.startswith('//@') or line.startswith('int ') or line.startswith('void '):
                in_code_block = True
            
            # If we're in code block, keep the line
            if in_code_block:
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        
        # Final cleanup - remove any remaining markdown artifacts
        result = result.replace('```', '').strip()
        
        return result
    
    def convert_file(self, dafny_file, output_dir, **kwargs) -> ConversionResult:
        """Convert a Dafny file to C"""
        try:
            with open(dafny_file, 'r', encoding='utf-8') as f:
                dafny_code = f.read()
            
            result = self.convert(dafny_code, **kwargs)
            
            if result.success:
                # Save the converted C code
                output_dir.mkdir(parents=True, exist_ok=True)
                c_file = output_dir / f"{dafny_file.stem}.c"
                
                with open(c_file, 'w', encoding='utf-8') as f:
                    f.write(result.c_code)
                
                # Save test file if generated
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
                error_message=f"File conversion failed: {str(e)}"
            )
    
    def get_version(self) -> str:
        """Get converter version"""
        return "1.0.0"
    
    def batch_convert(self, dafny_files: list[Path], output_dir: Path, **kwargs) -> list[ConversionResult]:
        """Convert multiple Dafny files"""
        results = []
        for dafny_file in dafny_files:
            try:
                result = self.convert_file(dafny_file, output_dir, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to convert {dafny_file}: {str(e)}")
                results.append(ConversionResult(
                    success=False,
                    error_message=f"Failed to convert {dafny_file}: {str(e)}"
                ))
        return results
    
    def get_supported_features(self) -> list[str]:
        """Get supported features"""
        return [
            "dafny_to_c_conversion",
            "acsl_annotations",
            "self_review",
            "test_generation",
            "code_cleaning"
        ] 