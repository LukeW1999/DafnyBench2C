#!/usr/bin/env python3
"""
Batch conversion script with progress tracking and resume capability
"""

import argparse
import getpass
from pathlib import Path
from typing import List
from src.core.services import ServiceFactory
from src.config import get_settings
from src.utils.batch_manager import BatchManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

def get_dafny_files(input_dir: Path, limit: int = None) -> List[Path]:
    """Get Dafny file list"""
    dafny_files = list(input_dir.glob("**/*.dfy"))
    
    if limit:
        dafny_files = dafny_files[:limit]
    
    return dafny_files

def run_batch_conversion(batch_name: str, input_dir: Path, output_dir: Path, 
                        converter_type: str = "deepseek", limit: int = None,
                        resume: bool = True, reset_failed: bool = False):
    """Run batch conversion"""
    
    # Get settings and API key
    settings = get_settings()
    if not settings.api_key:
        if converter_type == "deepseek":
            api_key = getpass.getpass("Please enter your DeepSeek API key: ")
        else:
            api_key = getpass.getpass("Please enter your Claude API key: ")
        settings.api_key = api_key
    
    # Create conversion service
    service = ServiceFactory.create_conversion_service(
        converter_type=converter_type,
        validator_type='heuristic',
        tester_type='gcc',
        save_results=True
    )
    
    # Create batch manager
    batch_manager = BatchManager(batch_name, output_dir)
    
    # Get Dafny files
    dafny_files = get_dafny_files(input_dir, limit)
    logger.info(f"Found {len(dafny_files)} Dafny files")
    
    # Add files to batch
    batch_manager.add_files(dafny_files)
    
    # Reset failed files (if needed)
    if reset_failed:
        batch_manager.reset_failed_files()
    
    # Show initial progress
    batch_manager.print_progress()
    
    # Get files to process
    files_to_process = batch_manager.get_pending_files()
    
    if not files_to_process:
        logger.info("No files to process!")
        return
    
    logger.info(f"Starting batch conversion of {len(files_to_process)} files")
    
    # Process each file
    for i, item in enumerate(files_to_process, 1):
        input_file = Path(item.input_file)
        output_path = Path(item.output_dir)
        
        logger.info(f"Processing file {i}/{len(files_to_process)}: {input_file.name}")
        logger.info(f"Output directory: {output_path}")
        
        try:
            # Mark as running
            batch_manager.mark_running(item.input_file)
            
            # Run conversion
            result = service.convert_single_file(input_file, output_path)
            
            # Check result
            if result.conversion.success:
                validation_score = result.validation.score if result.validation else 0.0
                test_success = result.testing.success if result.testing else False
                
                # Mark as completed
                batch_manager.mark_completed(
                    item.input_file,
                    conversion_score=1.0 if result.conversion.success else 0.0,
                    validation_score=validation_score,
                    test_success=test_success,
                    notes=f"Successfully converted with validation score {validation_score:.3f}"
                )
                
                logger.info(f"✅ Completed: {input_file.name} (Score: {validation_score:.3f})")
            else:
                # Mark as failed
                batch_manager.mark_failed(
                    item.input_file,
                    error_message=result.conversion.error_message or "Unknown error",
                    notes="Conversion failed"
                )
                
                logger.error(f"❌ Failed: {input_file.name} - {result.conversion.error_message}")
        
        except Exception as e:
            # Mark as failed
            batch_manager.mark_failed(
                item.input_file,
                error_message=str(e),
                notes=f"Exception: {type(e).__name__}"
            )
            
            logger.error(f"❌ Exception: {input_file.name} - {str(e)}")
        
        # Show progress every 5 files
        if i % 5 == 0 or i == len(files_to_process):
            batch_manager.print_progress()
    
    # Show final progress
    batch_manager.print_progress()
    
    # Export detailed results
    detailed_results = batch_manager.export_detailed_results()
    logger.info(f"Detailed results exported to: {detailed_results}")
    
    # Create README file
    readme_path = batch_manager.create_readme()
    logger.info(f"README created at: {readme_path}")
    
    # Show final statistics
    print(f"\n🎉 Batch conversion completed!")
    print(f"📁 Results saved to: {output_dir}")
    print(f"📊 Summary: {detailed_results}")
    print(f"📖 Documentation: {readme_path}")

def main():
    parser = argparse.ArgumentParser(description="Batch Dafny to C conversion with progress tracking")
    parser.add_argument("--input-dir", type=Path, default="DafnyBench/DafnyBench/dataset/ground_truth",
                       help="Input directory containing Dafny files")
    parser.add_argument("--output-dir", type=Path, default="batch_results",
                       help="Output directory for results")
    parser.add_argument("--batch-name", type=str, default="batch_001",
                       help="Batch name for progress tracking")
    parser.add_argument("--converter", type=str, default="deepseek",
                       choices=["deepseek", "claude"], help="Converter type")
    parser.add_argument("--limit", type=int, default=10,
                       help="Limit number of files to process")
    parser.add_argument("--resume", action="store_true", default=True,
                       help="Resume from previous progress")
    parser.add_argument("--reset-failed", action="store_true",
                       help="Reset failed files to pending status")
    
    args = parser.parse_args()
    
    # Validate input directory
    if not args.input_dir.exists():
        logger.error(f"Input directory does not exist: {args.input_dir}")
        return
    
    # Run batch conversion
    run_batch_conversion(
        batch_name=args.batch_name,
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        converter_type=args.converter,
        limit=args.limit,
        resume=args.resume,
        reset_failed=args.reset_failed
    )

if __name__ == "__main__":
    main() 