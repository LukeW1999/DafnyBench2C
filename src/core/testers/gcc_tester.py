"""
GCC-based tester implementation
"""

import os
import re
import csv
import tempfile
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from src.interfaces import ITester, TestResult
from src.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GCCTester(ITester):
    """GCC-based tester for C code compilation and execution"""
    
    def __init__(self, timeout: Optional[int] = None):
        self.settings = get_settings()
        self.compilation_timeout = timeout or self.settings.compilation_timeout
        self.execution_timeout = self.settings.execution_timeout
        logger.info("Initialized GCCTester")
    
    def compile_and_test(self, c_file: Path, **kwargs) -> TestResult:
        """Compile and test a C file"""
        logger.info(f"Starting compilation and testing for {c_file}")
        
        try:
            # Create temporary executable file
            with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_exe:
                exe_path = tmp_exe.name
            
            # Compile the C file
            compile_result = self._compile_c_file(c_file, exe_path)
            if not compile_result['success']:
                return TestResult(
                    success=False,
                    compiles=False,
                    runs=False,
                    error=compile_result['error']
                )
            
            # Execute the compiled program
            execution_result = self._execute_program(exe_path)
            
            # Parse test results
            test_results = self.analyze_results(execution_result['output'])
            
            # Save results to CSV if enabled
            csv_file = None
            if self.settings.enable_csv_output:
                csv_file = self.save_results_csv(
                    TestResult(
                        success=execution_result['success'],
                        compiles=True,
                        runs=execution_result['success'],
                        output=execution_result['output'],
                        error=execution_result['error'],
                        test_results=test_results
                    ),
                    c_file.parent / f"{c_file.stem}_results.csv"
                )
            
            return TestResult(
                success=execution_result['success'],
                compiles=True,
                runs=execution_result['success'],
                output=execution_result['output'],
                error=execution_result['error'],
                test_results=test_results,
                csv_file=csv_file
            )
            
        except Exception as e:
            logger.error(f"Testing failed: {str(e)}")
            return TestResult(
                success=False,
                compiles=False,
                runs=False,
                error=str(e)
            )
        finally:
            # Clean up temporary executable
            try:
                if 'exe_path' in locals():
                    os.unlink(exe_path)
            except OSError:
                pass
    
    def generate_tests(self, c_code: str, **kwargs) -> str:
        """Generate test cases for C code"""
        # This would typically use an AI model to generate tests
        # For now, return a basic test template
        test_template = f"""
#include <stdio.h>
#include <assert.h>

{c_code}

int main() {{
    printf("Running tests...\\n");
    
    // Test case 1: Basic functionality
    // TODO: Add specific test cases based on the C code
    
    printf("All tests passed!\\n");
    return 0;
}}
"""
        return test_template
    
    def analyze_results(self, test_output: str, **kwargs) -> Dict[str, Any]:
        """Analyze test results from output"""
        logger.info("Analyzing test results")
        
        results = []
        lines = test_output.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if 'Test case' in line and 'passed' in line:
                results.append({
                    'test_number': i + 1,
                    'status': 'PASSED',
                    'message': line
                })
            elif 'Test case' in line and 'failed' in line:
                results.append({
                    'test_number': i + 1,
                    'status': 'FAILED',
                    'message': line
                })
        
        return {
            'total_tests': len(results),
            'passed_tests': len([r for r in results if r['status'] == 'PASSED']),
            'failed_tests': len([r for r in results if r['status'] == 'FAILED']),
            'test_details': results
        }
    
    def save_results_csv(self, test_result: TestResult, output_path: Path) -> Path:
        """Save test results to CSV"""
        logger.info(f"Saving results to {output_path}")
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Test_File', 'Stage', 'Status', 'Details'])
                
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Write compilation result
                writer.writerow([
                    timestamp,
                    test_result.metadata.get('test_file', 'unknown'),
                    'Compilation',
                    'SUCCESS' if test_result.compiles else 'FAILED',
                    ''
                ])
                
                # Write execution result
                writer.writerow([
                    timestamp,
                    test_result.metadata.get('test_file', 'unknown'),
                    'Execution',
                    'SUCCESS' if test_result.runs else 'FAILED',
                    test_result.error or ''
                ])
                
                # Write individual test results
                for test_detail in test_result.test_results:
                    writer.writerow([
                        timestamp,
                        test_result.metadata.get('test_file', 'unknown'),
                        f'Test_{test_detail["test_number"]}',
                        test_detail['status'],
                        test_detail['message']
                    ])
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to save CSV results: {str(e)}")
            return None
    
    def _compile_c_file(self, c_file: Path, exe_path: str) -> Dict[str, Any]:
        """Compile C file using GCC"""
        logger.info(f"Compiling {c_file}")
        
        try:
            result = subprocess.run(
                ['gcc', '-o', exe_path, str(c_file), '-Wall', '-Wextra'],
                capture_output=True,
                text=True,
                timeout=self.compilation_timeout
            )
            
            if result.returncode == 0:
                logger.info("Compilation successful")
                return {'success': True}
            else:
                error_msg = result.stderr.strip()
                logger.error(f"Compilation failed: {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except subprocess.TimeoutExpired:
            error_msg = f"Compilation timeout after {self.compilation_timeout} seconds"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Compilation error: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def _execute_program(self, exe_path: str) -> Dict[str, Any]:
        """Execute compiled program"""
        logger.info(f"Executing {exe_path}")
        
        try:
            result = subprocess.run(
                [exe_path],
                capture_output=True,
                text=True,
                timeout=self.execution_timeout
            )
            
            if result.returncode == 0:
                logger.info("Execution successful")
                return {
                    'success': True,
                    'output': result.stdout.strip(),
                    'error': None
                }
            else:
                error_msg = result.stderr.strip()
                logger.error(f"Execution failed: {error_msg}")
                return {
                    'success': False,
                    'output': result.stdout.strip(),
                    'error': error_msg
                }
                
        except subprocess.TimeoutExpired:
            error_msg = f"Execution timeout after {self.execution_timeout} seconds"
            logger.error(error_msg)
            return {
                'success': False,
                'output': '',
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'output': '',
                'error': error_msg
            } 