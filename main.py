#!/usr/bin/env python3
"""
DafnyBench2C - Main entry point (Refactored)
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.services import ServiceFactory
from src.config import get_settings, update_settings
from src.utils.logger import get_logger, set_log_level, LogLevel

def main():
    parser = argparse.ArgumentParser(
        description="DafnyBench2C - Convert Dafny code to C with verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test single file conversion with Claude
  python main.py test-single --api-key YOUR_CLAUDE_KEY
  
  # Test batch conversion (10 files) with DeepSeek
  python main.py test-batch --api-key YOUR_DEEPSEEK_KEY --converter deepseek --model deepseek-chat
  
  # Convert single file with Claude
  python main.py convert --api-key YOUR_CLAUDE_KEY --input-file path/to/file.dfy
  
  # Convert single file with DeepSeek
  python main.py convert --api-key YOUR_DEEPSEEK_KEY --converter deepseek --model deepseek-chat --input-file path/to/file.dfy
  
  # Convert directory with DeepSeek Reasoner
  python main.py convert --api-key YOUR_DEEPSEEK_KEY --converter deepseek --model deepseek-reasoner --input-dir path/to/directory
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test single file
    test_single_parser = subparsers.add_parser('test-single', help='Test single file conversion')
    test_single_parser.add_argument('--api-key', required=True, help='Claude API key')
    
    # Test batch
    test_batch_parser = subparsers.add_parser('test-batch', help='Test batch conversion (10 files)')
    test_batch_parser.add_argument('--api-key', required=True, help='Claude API key')
    
    # Convert
    convert_parser = subparsers.add_parser('convert', help='Convert Dafny files to C')
    convert_parser.add_argument('--api-key', help='Claude API key (or set CLAUDE_API_KEY env var)')
    convert_parser.add_argument('--input-file', help='Single Dafny file path')
    convert_parser.add_argument('--input-dir', help='Directory containing Dafny files')
    convert_parser.add_argument('--output-dir', default='converted_c', help='Output directory for C files')
    convert_parser.add_argument('--test-dir', default='test_cases', help='Output directory for test files')
    convert_parser.add_argument('--model', default='claude-3-opus-20240229', help='Model name (claude-3-opus-20240229, deepseek-chat, deepseek-reasoner)')
    convert_parser.add_argument('--converter', default='claude', help='Converter type (claude, deepseek)')
    convert_parser.add_argument('--validator', default='heuristic', help='Validator type')
    convert_parser.add_argument('--tester', default='gcc', help='Tester type')
    convert_parser.add_argument('--save-results', action='store_true', default=True, help='Save detailed results to files')
    convert_parser.add_argument('--no-save-results', dest='save_results', action='store_false', help='Disable result saving')
    
    # Status
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    logger = get_logger(__name__)
    if args.verbose:
        set_log_level(LogLevel.DEBUG)
    
    # Update settings
    if hasattr(args, 'api_key') and args.api_key:
        update_settings(api_key=args.api_key)
    
    if args.command == 'test-single':
        # Test single file conversion
        logger.info("Starting single file test")
        _run_single_test()
        
    elif args.command == 'test-batch':
        # Test batch conversion
        logger.info("Starting batch test")
        _run_batch_test()
        
    elif args.command == 'convert':
        # Run conversion
        logger.info("Starting conversion")
        _run_conversion(args)
        
    elif args.command == 'status':
        # Show system status
        _show_status()
        
    else:
        print("❌ Please specify a valid command")

def _run_single_test():
    """Run single file test"""
    import getpass
    from src.tests.test_conversion import test_single_file
    
    settings = get_settings()
    if not settings.api_key:
        settings.api_key = getpass.getpass("Please enter your Claude API key: ")
    
    test_single_file()

def _run_batch_test():
    """Run batch test"""
    import getpass
    from src.tests.test_10_files_with_tests import test_10_files
    
    settings = get_settings()
    if not settings.api_key:
        settings.api_key = getpass.getpass("Please enter your Claude API key: ")
    
    test_10_files()

def _run_conversion(args):
    """Run conversion with specified parameters"""
    import getpass
    settings = get_settings()
    
    # Check if API key is available
    if not settings.api_key:
        if args.converter == 'deepseek':
            settings.api_key = getpass.getpass("Please enter your DeepSeek API key: ")
        else:
            settings.api_key = getpass.getpass("Please enter your Claude API key: ")
    
    # Create service
    service = ServiceFactory.create_conversion_service(
        converter_type=args.converter,
        validator_type=args.validator,
        tester_type=args.tester,
        api_key=settings.api_key,
        model=args.model,
        save_results=args.save_results
    )
    
    if args.input_file:
        # Single file conversion
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"❌ Input file does not exist: {args.input_file}")
            return
        
        output_dir = Path(args.output_dir)
        test_dir = Path(args.test_dir) if args.test_dir else None
        
        result = service.convert_single_file(input_path, output_dir, test_dir)
        
        if result.conversion.success:
            print("🎉 Single file conversion completed!")
            if result.validation:
                print(f"📊 Validation score: {result.validation.score:.2f}")
            if result.testing:
                print(f"🧪 Testing: {'✅ Passed' if result.testing.success else '❌ Failed'}")
        else:
            print(f"💥 Single file conversion failed: {result.conversion.error_message}")
            
    elif args.input_dir:
        # Batch conversion
        input_path = Path(args.input_dir)
        if not input_path.exists():
            print(f"❌ Input directory does not exist: {args.input_dir}")
            return
        
        dafny_files = list(input_path.glob("*.dfy"))
        if not dafny_files:
            print(f"❌ No .dfy files found in directory {args.input_dir}")
            return
        
        print(f"📁 Found {len(dafny_files)} Dafny files")
        
        output_dir = Path(args.output_dir)
        test_dir = Path(args.test_dir) if args.test_dir else None
        
        results = service.batch_convert(dafny_files, output_dir, test_dir)
        
        successful = sum(1 for r in results if r.conversion.success)
        print(f"🎉 Batch conversion completed! Successfully converted {successful}/{len(dafny_files)} files")
        
    else:
        print("❌ Please specify --input-file or --input-dir parameter")

def _show_status():
    """Show system status"""
    settings = get_settings()
    
    print("🔧 DafnyBench2C System Status")
    print("=" * 50)
    
    # Configuration
    print(f"📋 API Key: {'✅ Set' if settings.api_key else '❌ Not set'}")
    print(f"🤖 Model: {settings.model}")
    print(f"📁 Output Directory: {settings.output_dir}")
    print(f"🧪 Test Directory: {settings.test_dir}")
    
    # Available components
    from src.core.converters import ConverterFactory
    from src.core.validators import ValidatorFactory
    from src.core.testers import TesterFactory
    
    print(f"🔄 Available Converters: {', '.join(ConverterFactory.get_available_converters())}")
    print(f"🤖 Available Models:")
    print(f"  Claude: claude-3-opus-20240229, claude-3-sonnet-20240229")
    print(f"  DeepSeek: deepseek-chat, deepseek-reasoner")
    print(f"✅ Available Validators: {', '.join(ValidatorFactory.get_available_validators())}")
    print(f"🧪 Available Testers: {', '.join(TesterFactory.get_available_testers())}")
    
    # Create service to show pipeline status
    try:
        service = ServiceFactory.create_default_service()
        status = service.get_pipeline_status()
        
        print("\n🔗 Pipeline Status:")
        print(f"  Converter: {status['converter']['type']} v{status['converter']['version']}")
        print(f"  Validator: {status['validator']['type']}")
        print(f"  Tester: {status['tester']['type']}")
        
    except Exception as e:
        print(f"⚠️  Could not initialize pipeline: {e}")

if __name__ == "__main__":
    main() 