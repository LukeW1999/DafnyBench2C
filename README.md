# DafnyBench2C: Dafny to C Conversion Tool

A comprehensive tool for converting Dafny formal verification code to C with ACSL annotations, featuring AI-powered conversion, automated testing, and heuristic validation.

## 🚀 Features

- **AI-Powered Conversion**: Uses DeepSeek or Claude AI models for intelligent Dafny-to-C conversion
- **ACSL Annotation Preservation**: Maintains formal verification contracts from Dafny to C
- **Automated Testing**: Generates and runs test cases for converted C code
- **Heuristic Validation**: Rule-based scoring system for conversion quality assessment
- **Batch Processing**: Handle large datasets with progress tracking and resume capability
- **Detailed Reporting**: Comprehensive results in JSON and CSV formats

## 📋 Requirements

- Python 3.8+
- GCC compiler
- DeepSeek API key or Claude API key

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/DafnyBench2C.git
   cd DafnyBench2C
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key**:
   ```bash
   export DEEPSEEK_API_KEY="your_api_key_here"
   # or
   export CLAUDE_API_KEY="your_api_key_here"
   ```

## 🎯 Quick Start

### Single File Conversion

```bash
# Convert a single Dafny file
python main.py convert --input DafnyBench/dataset/ground_truth/Clover_abs.dfy --output converted_output --converter deepseek
```

### Batch Processing

```bash
# Process 10 files with progress tracking
python batch_convert.py --limit 10 --batch-name "test_batch"

# Process more files
python batch_convert.py --limit 50 --batch-name "large_batch"
```

## 📁 Project Structure

```
DafnyBench2C/
├── src/
│   ├── core/
│   │   ├── converters/     # AI model converters
│   │   ├── validators/     # Validation logic
│   │   ├── testers/        # Testing framework
│   │   └── services/       # Service orchestration
│   ├── config/             # Configuration management
│   ├── interfaces/         # Abstract interfaces
│   └── utils/              # Utility functions
├── DafnyBench/             # Dafny dataset
├── batch_results/          # Batch processing results
├── main.py                 # Single file conversion CLI
├── batch_convert.py        # Batch processing script
└── README.md
```

## 🔧 Configuration

### Supported Converters

- **DeepSeek**: `deepseek-chat` model (recommended)
- **Claude**: `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku`

### Validation Rules

The system evaluates conversion quality based on:
- **Function Signatures** (25%): Method name preservation
- **ACSL Annotations** (35%): Contract clause conversion
- **Tests Passed** (40%): Compilation and execution success

## 📊 Output Structure

Batch processing creates a clear directory structure:

```
batch_results/
├── converted/              # Converted C code files
│   ├── file1/             # Each Dafny file gets its own directory
│   │   ├── main.c         # Converted C code
│   │   └── test.c         # Generated test file
│   └── file2/
├── reports/               # Progress and statistics
│   ├── batch_progress.json
│   ├── batch_summary.csv
│   └── detailed_results.csv
└── README.md              # Batch-specific documentation
```

## 🚀 Advanced Usage

### Resume Interrupted Batch

```bash
# Continue from where you left off
python batch_convert.py --batch-name "test_batch"
```

### Reset Failed Files

```bash
# Retry failed conversions
python batch_convert.py --batch-name "test_batch" --reset-failed
```

### Different Converter

```bash
# Use Claude instead of DeepSeek
python batch_convert.py --converter claude --limit 10
```

## 📈 Results Interpretation

### Validation Scores

- **0.0-0.5**: Poor conversion quality
- **0.5-0.8**: Good conversion quality
- **0.8-1.0**: Excellent conversion quality

### Test Results

- **True**: Tests compiled and executed successfully
- **False**: Compilation or execution failed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- DafnyBench dataset for providing the Dafny code samples
- DeepSeek and Anthropic for AI model APIs
- The formal verification community for inspiration

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the [USAGE.md](USAGE.md) for detailed usage examples
