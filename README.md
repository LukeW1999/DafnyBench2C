# DafnyBench2C: AI-Powered Dafny to C Conversion Tool

A comprehensive tool for converting Dafny programs to C with formal verification annotations (ACSL), featuring AI model support, automated testing, and detailed validation.

## 🚀 Features

- **AI-Powered Conversion**: Support for Claude and DeepSeek models
- **Formal Verification**: ACSL annotations for C programs
- **Automated Testing**: Compilation and execution testing
- **Heuristic Validation**: Rule-based conversion quality assessment
- **Batch Processing**: Handle multiple files with progress tracking
- **Detailed Reporting**: Comprehensive results and analysis

## 📋 Prerequisites

- Python 3.8+
- GCC compiler
- API keys for AI models (Claude or DeepSeek)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd DafnyBench2C
   ```

2. **Initialize and update submodules**:
   ```bash
   git submodule update --init --recursive
   ```
   
   The project uses the DafnyBench dataset as a git submodule:
   - `DafnyBench/DafnyBench/dataset/ground_truth/`: Original Dafny files with hints
   - `DafnyBench/DafnyBench/dataset/hints_removed/`: Dafny files with hints removed
   - `DafnyBench/DafnyBench/dataset/metadata.json`: Dataset metadata
   - `DafnyBench/DafnyBench/dataset/test.json`: Test configuration

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Quick Start

### Single File Conversion

```bash
python main.py --input DafnyBench/DafnyBench/dataset/ground_truth/Clover_binary_search.dfy --converter claude
```

### Batch Processing

```bash
python batch_convert.py --input-dir DafnyBench/DafnyBench/dataset/ground_truth --converter deepseek
```

## 📁 Project Structure

```
DafnyBench2C/
├── src/                    # Core source code
│   ├── config/            # Configuration management
│   ├── core/              # Main conversion logic
│   │   ├── converters/    # AI model converters
│   │   ├── services/      # Business logic services
│   │   ├── testers/       # Testing components
│   │   └── validators/    # Validation components
│   ├── interfaces/        # Abstract interfaces
│   └── utils/             # Utility functions
├── DafnyBench/            # Dataset (git submodule)
│   ├── dataset/
│   │   ├── ground_truth/  # Original Dafny files
│   │   └── hints_removed/ # Files without hints
│   └── metadata/          # Dataset metadata
├── results/               # Conversion results
├── main.py               # Single file conversion
├── batch_convert.py      # Batch processing
└── requirements.txt      # Python dependencies
```

## ⚙️ Configuration

### Environment Variables

```bash
export CLAUDE_API_KEY="your-claude-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

### Configuration Files

- `src/config/settings.py`: Global settings
- `src/config/models.py`: AI model configurations

## 📊 Output Interpretation

### Validation Scores

- **Function Signatures (25%)**: Parameter and return type matching
- **ACSL Annotations (35%)**: Formal specification conversion quality
- **Tests Passed (40%)**: Compilation and execution success rate

### Result Files

- `converted/`: Generated C files
- `reports/`: Detailed analysis reports
- `results/`: JSON and CSV result summaries

## 🔧 Advanced Usage

### Custom Converters

```python
from src.core.converters.converter_factory import ConverterFactory

converter = ConverterFactory.create_converter('claude', api_key='your-key')
result = converter.convert_dafny_to_c(dafny_code)
```

### Batch Processing Options

```bash
# Resume interrupted batch
python batch_convert.py --resume

# Reset failed conversions
python batch_convert.py --reset-failed

# Custom output directory
python batch_convert.py --output-dir ./my_results
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DafnyBench Dataset**: This project uses the [DafnyBench](https://github.com/sun-wendy/DafnyBench) dataset as a git submodule for evaluation and testing purposes.
- **Claude API**: Powered by Anthropic's Claude models
- **DeepSeek API**: Powered by DeepSeek's AI models

## 📞 Support

For questions and support, please open an issue on GitHub.

---

**Note**: The DafnyBench dataset is included as a git submodule. If you clone this repository, make sure to run `git submodule update --init --recursive` to download the dataset files.
