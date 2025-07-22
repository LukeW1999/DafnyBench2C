"""
Result saver for conversion pipeline results
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.interfaces.results import ConversionPipelineResult
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ResultSaver:
    """Save conversion pipeline results to files"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create results subdirectories
        self.csv_dir = self.output_dir / "results_csv"
        self.json_dir = self.output_dir / "results_json"
        self.csv_dir.mkdir(exist_ok=True)
        self.json_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized ResultSaver in {self.output_dir}")
    
    def save_single_result(self, result: ConversionPipelineResult, filename: str = None) -> Path:
        """Save a single conversion result"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"result_{timestamp}"
        
        # Save detailed JSON result
        json_file = self.json_dir / f"{filename}.json"
        self._save_json_result(result, json_file)
        
        # Save CSV summary
        csv_file = self.csv_dir / f"{filename}.csv"
        self._save_csv_result([result], csv_file)
        
        logger.info(f"Saved result to {json_file} and {csv_file}")
        return json_file
    
    def save_batch_results(self, results: List[ConversionPipelineResult], batch_name: str = None) -> Path:
        """Save batch conversion results"""
        if batch_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_name = f"batch_{timestamp}"
        
        # Save detailed JSON results
        json_file = self.json_dir / f"{batch_name}_results.json"
        self._save_json_batch_results(results, json_file)
        
        # Save CSV summary
        csv_file = self.csv_dir / f"{batch_name}_summary.csv"
        self._save_csv_result(results, csv_file)
        
        # Save detailed CSV with all results
        detailed_csv_file = self.csv_dir / f"{batch_name}_detailed.csv"
        self._save_detailed_csv_results(results, detailed_csv_file)
        
        logger.info(f"Saved batch results to {json_file}, {csv_file}, and {detailed_csv_file}")
        return json_file
    
    def _save_json_result(self, result: ConversionPipelineResult, filepath: Path):
        """Save single result as JSON"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'conversion': {
                'success': result.conversion.success,
                'error_message': result.conversion.error_message,
                'metadata': result.conversion.metadata
            },
            'validation': {
                'score': result.validation.score if result.validation else None,
                'is_valid': result.validation.is_valid if result.validation else None,
                'details': result.validation.details if result.validation else [],
                'issues': result.validation.issues if result.validation else [],
                'metadata': result.validation.metadata if result.validation else {}
            },
            'testing': {
                'success': result.testing.success if result.testing else None,
                'output': result.testing.output if result.testing else None,
                'error': result.testing.error if result.testing else None,
                'metadata': result.testing.metadata if result.testing else {}
            },
            'metadata': result.metadata
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_json_batch_results(self, results: List[ConversionPipelineResult], filepath: Path):
        """Save batch results as JSON"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files': len(results),
                'successful_conversions': sum(1 for r in results if r.conversion.success),
                'average_validation_score': self._calculate_average_score(results),
                'successful_tests': sum(1 for r in results if r.testing and r.testing.success)
            },
            'results': []
        }
        
        for i, result in enumerate(results):
            result_data = {
                'index': i,
                'conversion': {
                    'success': result.conversion.success,
                    'error_message': result.conversion.error_message,
                    'metadata': result.conversion.metadata
                },
                'validation': {
                    'score': result.validation.score if result.validation else None,
                    'is_valid': result.validation.is_valid if result.validation else None,
                    'details': result.validation.details if result.validation else [],
                    'issues': result.validation.issues if result.validation else [],
                    'metadata': result.validation.metadata if result.validation else {}
                },
                'testing': {
                    'success': result.testing.success if result.testing else None,
                    'output': result.testing.output if result.testing else None,
                    'error': result.testing.error if result.testing else None,
                    'metadata': result.testing.metadata if result.testing else {}
                },
                'metadata': result.metadata
            }
            data['results'].append(result_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_csv_result(self, results: List[ConversionPipelineResult], filepath: Path):
        """Save results summary as CSV"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Timestamp',
                'Input_File',
                'Conversion_Success',
                'Validation_Score',
                'Validation_Valid',
                'Testing_Success',
                'Error_Message'
            ])
            
            # Write data
            for result in results:
                input_file = result.metadata.get('input_file', 'Unknown') if result.metadata else 'Unknown'
                writer.writerow([
                    datetime.now().isoformat(),
                    input_file,
                    result.conversion.success,
                    f"{result.validation.score:.3f}" if result.validation else "N/A",
                    result.validation.is_valid if result.validation else "N/A",
                    result.testing.success if result.testing else "N/A",
                    result.conversion.error_message or "N/A"
                ])
    
    def _save_detailed_csv_results(self, results: List[ConversionPipelineResult], filepath: Path):
        """Save detailed results as CSV with validation scores and reasons"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Index',
                'Timestamp',
                'Input_File',
                'Conversion_Success',
                'Validation_Score',
                'Validation_Valid',
                'Function_Signatures_Score',
                'ACSL_Annotations_Score',
                'Tests_Passed_Score',
                'Validation_Details',
                'Validation_Issues',
                'Function_Signatures_Reasons',
                'ACSL_Annotations_Reasons',
                'Tests_Passed_Reasons',
                'Testing_Success',
                'Testing_Output',
                'Testing_Error',
                'Error_Message'
            ])
            
            # Write data
            for i, result in enumerate(results):
                input_file = result.metadata.get('input_file', 'Unknown') if result.metadata else 'Unknown'
                validation_details = '; '.join(result.validation.details) if result.validation else "N/A"
                validation_issues = '; '.join(result.validation.issues) if result.validation else "N/A"
                testing_output = result.testing.output[:200] + "..." if result.testing and result.testing.output else "N/A"
                
                # Extract detailed scores and reasons
                detailed_scores = result.validation.metadata.get('detailed_scores', {}) if result.validation else {}
                validation_reasons = result.validation.metadata.get('validation_reasons', {}) if result.validation else {}
                
                # Format reasons for CSV
                def format_reasons(category):
                    if category in validation_reasons:
                        reasons = validation_reasons[category].get('reasons', [])
                        return '; '.join(reasons[:3])  # Limit to first 3 reasons
                    return "N/A"
                
                writer.writerow([
                    i,
                    datetime.now().isoformat(),
                    input_file,
                    result.conversion.success,
                    f"{result.validation.score:.3f}" if result.validation else "N/A",
                    result.validation.is_valid if result.validation else "N/A",
                    f"{detailed_scores.get('function_signatures', 0.0):.3f}",
                    f"{detailed_scores.get('acsl_annotations', 0.0):.3f}",
                    f"{detailed_scores.get('tests_passed', 0.0):.3f}",
                    validation_details,
                    validation_issues,
                    format_reasons('function_signatures'),
                    format_reasons('acsl_annotations'),
                    format_reasons('tests_passed'),
                    result.testing.success if result.testing else "N/A",
                    testing_output,
                    result.testing.error if result.testing else "N/A",
                    result.conversion.error_message or "N/A"
                ])
    
    def _calculate_average_score(self, results: List[ConversionPipelineResult]) -> float:
        """Calculate average validation score"""
        scores = [r.validation.score for r in results if r.validation]
        return sum(scores) / len(scores) if scores else 0.0
    
    def generate_summary_report(self, results: List[ConversionPipelineResult], report_name: str = None) -> Path:
        """Generate a comprehensive summary report with detailed validation scores"""
        if report_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"summary_report_{timestamp}"
        
        report_file = self.output_dir / f"{report_name}.txt"
        
        successful_conversions = sum(1 for r in results if r.conversion.success)
        successful_tests = sum(1 for r in results if r.testing and r.testing.success)
        validation_scores = [r.validation.score for r in results if r.validation]
        avg_score = sum(validation_scores) / len(validation_scores) if validation_scores else 0.0
        
        # Calculate average detailed scores
        detailed_score_sums = {
            'function_signatures': 0.0,
            'acsl_annotations': 0.0,
            'type_conversion': 0.0,
            'logic_structure': 0.0,
            'array_handling': 0.0,
            'loop_conversion': 0.0,
            'tests_passed': 0.0
        }
        detailed_score_count = 0
        
        for result in results:
            if result.validation and result.validation.metadata:
                detailed_scores = result.validation.metadata.get('detailed_scores', {})
                if detailed_scores:
                    detailed_score_count += 1
                    for key in detailed_score_sums:
                        detailed_score_sums[key] += detailed_scores.get(key, 0.0)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("DafnyBench2C Conversion Summary Report\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Files Processed: {len(results)}\n")
            f.write(f"Successful Conversions: {successful_conversions} ({successful_conversions/len(results)*100:.1f}%)\n")
            f.write(f"Successful Tests: {successful_tests} ({successful_tests/len(results)*100:.1f}%)\n")
            f.write(f"Average Validation Score: {avg_score:.3f}\n")
            
            if detailed_score_count > 0:
                f.write("\n" + "=" * 60 + "\n")
                f.write("Average Detailed Validation Scores:\n")
                f.write("=" * 60 + "\n")
                score_names = {
                    'function_signatures': 'Function Signatures',
                    'acsl_annotations': 'ACSL Annotations',
                    'type_conversion': 'Type Conversion',
                    'logic_structure': 'Logic Structure',
                    'array_handling': 'Array Handling',
                    'loop_conversion': 'Loop Conversion',
                    'tests_passed': 'Tests Passed'
                }
                for key, name in score_names.items():
                    avg_detail_score = detailed_score_sums[key] / detailed_score_count
                    f.write(f"{name:20}: {avg_detail_score:.3f}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("Validation Score Distribution:\n")
            score_ranges = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
            for low, high in score_ranges:
                count = sum(1 for score in validation_scores if low <= score < high)
                f.write(f"  {low:.1f}-{high:.1f}: {count} files\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("Failed Conversions:\n")
            failed_count = 0
            for i, result in enumerate(results):
                if not result.conversion.success:
                    failed_count += 1
                    input_file = result.metadata.get('input_file', 'Unknown') if result.metadata else 'Unknown'
                    f.write(f"  {i+1}. {input_file}: {result.conversion.error_message}\n")
            
            if failed_count == 0:
                f.write("  None - All conversions successful!\n")
        
        logger.info(f"Generated summary report: {report_file}")
        return report_file 