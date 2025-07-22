"""
Main conversion service that orchestrates the entire conversion process
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from src.interfaces import IConverter, IValidator, ITester, ConversionResult, ValidationResult, TestResult
from src.interfaces.results import ConversionPipelineResult
from src.config import get_settings, ConverterConfig, TestConfig
from src.utils.logger import get_logger
from src.core.converters import ConverterFactory
from src.core.validators import ValidatorFactory
from src.core.testers import TesterFactory
from src.utils.result_saver import ResultSaver

logger = get_logger(__name__)

class ConversionService:
    """Main service that orchestrates the conversion process"""
    
    def __init__(self, 
                 converter: Optional[IConverter] = None,
                 validator: Optional[IValidator] = None,
                 tester: Optional[ITester] = None,
                 converter_config: Optional[ConverterConfig] = None,
                 test_config: Optional[TestConfig] = None,
                 save_results: bool = True):
        
        self.settings = get_settings()
        
        # Initialize components
        self.converter = converter or ConverterFactory.create_converter()
        self.validator = validator or ValidatorFactory.create_validator()
        self.tester = tester or TesterFactory.create_tester()
        
        # Configuration
        self.converter_config = converter_config or ConverterConfig()
        self.test_config = test_config or TestConfig()
        
        # Result saving
        self.save_results = save_results
        self.result_saver = None
        
        logger.info("Initialized ConversionService")
    
    def convert_single_file(self, 
                           dafny_file: Path, 
                           output_dir: Path, 
                           test_dir: Optional[Path] = None,
                           **kwargs) -> ConversionPipelineResult:
        """Convert a single Dafny file with full pipeline"""
        logger.info(f"Starting conversion pipeline for {dafny_file}")
        
        try:
            # Step 1: Convert Dafny to C
            conversion_result = self.converter.convert_file(dafny_file, output_dir, **kwargs)
            if not conversion_result.success:
                logger.error(f"Conversion failed: {conversion_result.error_message}")
                return ConversionPipelineResult(conversion=conversion_result)
            
            # Step 2: Test the converted code first (if enabled)
            test_result = None
            test_score = 0.0
            if self.converter_config.enable_test_generation and conversion_result.test_code:
                logger.info("Starting testing")
                test_dir = test_dir or output_dir
                test_file = test_dir / f"test_{dafny_file.stem}.c"
                
                # Save test file
                test_dir.mkdir(parents=True, exist_ok=True)
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(conversion_result.test_code)
                
                # Run tests
                test_result = self.tester.compile_and_test(test_file)
                logger.info(f"Testing completed. Success: {test_result.success}")
                
                # Calculate test score
                if test_result.success:
                    test_score = 1.0
                elif test_result.error and "compilation" in test_result.error.lower():
                    test_score = 0.0
                else:
                    test_score = 0.5  # Partial success
            
            # Step 3: Validate conversion with test score (if enabled)
            validation_result = None
            if self.converter_config.enable_validation:
                logger.info("Starting validation")
                c_file = output_dir / f"{dafny_file.stem}.c"
                with open(c_file, 'r', encoding='utf-8') as f:
                    c_code = f.read()
                
                with open(dafny_file, 'r', encoding='utf-8') as f:
                    dafny_code = f.read()
                
                # 运行验证
                validation_result = self.validator.validate_conversion(
                    dafny_code=dafny_code,
                    c_code=conversion_result.c_code,
                    test_score=test_score,
                    compilation_timeout=self.test_config.compilation_timeout,
                    execution_timeout=self.test_config.execution_timeout
                )
                logger.info(f"Validation completed. Score: {validation_result.score:.2f}")
            
            result = ConversionPipelineResult(
                conversion=conversion_result,
                validation=validation_result,
                testing=test_result,
                metadata={
                    'input_file': str(dafny_file),
                    'output_dir': str(output_dir),
                    'test_dir': str(test_dir) if test_dir else None
                }
            )
            
            # Save result if enabled
            if self.save_results:
                if self.result_saver is None:
                    results_dir = output_dir / "results"
                    self.result_saver = ResultSaver(results_dir)
                
                filename = f"{dafny_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.result_saver.save_single_result(result, filename)
            
            return result
            
        except Exception as e:
            logger.error(f"Conversion pipeline failed: {str(e)}")
            return ConversionPipelineResult(
                conversion=ConversionResult(
                    success=False,
                    error_message=str(e)
                )
            )
    
    def batch_convert(self, 
                     dafny_files: List[Path], 
                     output_dir: Path,
                     test_dir: Optional[Path] = None,
                     **kwargs) -> List[ConversionPipelineResult]:
        """Convert multiple Dafny files"""
        logger.info(f"Starting batch conversion of {len(dafny_files)} files")
        
        results = []
        for i, dafny_file in enumerate(dafny_files, 1):
            logger.info(f"Processing file {i}/{len(dafny_files)}: {dafny_file.name}")
            result = self.convert_single_file(dafny_file, output_dir, test_dir, **kwargs)
            results.append(result)
        
        # Log summary
        successful = sum(1 for r in results if r.conversion.success)
        logger.info(f"Batch conversion completed. {successful}/{len(dafny_files)} successful")
        
        # Save batch results if enabled
        if self.save_results:
            if self.result_saver is None:
                results_dir = output_dir / "results"
                self.result_saver = ResultSaver(results_dir)
            
            batch_name = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.result_saver.save_batch_results(results, batch_name)
            
            # Generate summary report
            self.result_saver.generate_summary_report(results, f"summary_{batch_name}")
        
        return results
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status of all pipeline components"""
        return {
            'converter': {
                'type': type(self.converter).__name__,
                'version': self.converter.get_version(),
                'supported_features': self.converter.get_supported_features()
            },
            'validator': {
                'type': type(self.validator).__name__,
                'validation_rules': self.validator.get_validation_rules()
            },
            'tester': {
                'type': type(self.tester).__name__
            },
            'configuration': {
                'converter_config': {
                    'enable_self_review': self.converter_config.enable_self_review,
                    'enable_validation': self.converter_config.enable_validation,
                    'enable_test_generation': self.converter_config.enable_test_generation
                },
                'test_config': {
                    'compilation_timeout': self.test_config.compilation_timeout
                }
            }
        } 