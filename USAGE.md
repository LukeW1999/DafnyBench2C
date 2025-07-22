# DafnyBench2C Usage Guide

This document provides detailed usage examples and advanced configuration options for the DafnyBench2C tool.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Batch Processing](#batch-processing)
- [Configuration Options](#configuration-options)
- [Output Interpretation](#output-interpretation)
- [Troubleshooting](#troubleshooting)

## Basic Usage

### Single File Conversion

Convert a single Dafny file to C with ACSL annotations:

```bash
# Basic conversion with DeepSeek
python main.py convert \
  --input DafnyBench/DafnyBench/dataset/ground_truth/Clover_abs.dfy \
  --output converted_output \
  --converter deepseek

# Using Claude model
python main.py convert \
  --input DafnyBench/DafnyBench/dataset/ground_truth/Clover_abs.dfy \
  --output converted_output \
  --converter claude \
  --model claude-3-opus
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Input Dafny file path | Required |
| `--output` | Output directory | Required |
| `--converter` | AI model (deepseek/claude) | deepseek |
| `--model` | Specific model name | auto-detected |
| `--validator` | Validation method | heuristic |
| `--tester` | Testing method | gcc |
| `--save-results` | Save detailed results | True |
| `--no-save-results` | Disable result saving | False |

## Batch Processing

### Starting a New Batch

```bash
# Process 10 files
python batch_convert.py \
  --limit 10 \
  --batch-name "experiment_1" \
  --input-dir DafnyBench/DafnyBench/dataset/ground_truth \
  --output-dir batch_results

# Process with specific converter
python batch_convert.py \
  --limit 50 \
  --batch-name "claude_test" \
  --converter claude \
  --input-dir DafnyBench/DafnyBench/dataset/ground_truth
```

### Batch Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--limit` | Number of files to process | 10 |
| `--batch-name` | Batch identifier | batch_001 |
| `--input-dir` | Input directory | DafnyBench/DafnyBench/dataset/ground_truth |
| `--output-dir` | Output directory | batch_results |
| `--converter` | AI model | deepseek |
| `--resume` | Resume from previous run | True |
| `--reset-failed` | Retry failed files | False |

### Resuming Interrupted Batches

```bash
# Continue from where you left off
python batch_convert.py --batch-name "experiment_1"

# Reset and retry failed files
python batch_convert.py --batch-name "experiment_1" --reset-failed
```

## Configuration Options

### Environment Variables

Set API keys via environment variables:

```bash
# DeepSeek API
export DEEPSEEK_API_KEY="your_deepseek_api_key"

# Claude API
export CLAUDE_API_KEY="your_claude_api_key"
```

### Timeout Settings

Configure timeouts in `src/config/models.py`:

```python
@dataclass
class TestConfig:
    compilation_timeout: int = 60   # Compilation timeout (seconds)
    execution_timeout: int = 100    # Execution timeout (seconds)
```

### Validation Rules

Customize validation weights in `src/config/models.py`:

```python
validation_rules = {
    'function_signatures': 0.25,  # Method name preservation
    'acsl_annotations': 0.35,     # Contract clause conversion
    'tests_passed': 0.40          # Compilation/execution success
}
```

## Output Interpretation

### Batch Progress Display

```
============================================================
📊 Batch Progress: experiment_1
============================================================
📁 Total Files: 10
✅ Completed: 7 (70.0%)
❌ Failed: 2
⏳ Pending: 1
🔄 Running: 0
⏭️  Skipped: 0
📈 Average Validation Score: 0.823
🧪 Test Success Rate: 85.7%
🕒 Last Updated: 2025-07-22T15:30:00.000000
============================================================
```

### Validation Score Breakdown

- **Function Signatures (25%)**: Checks if method names are preserved
- **ACSL Annotations (35%)**: Evaluates contract clause conversion quality
- **Tests Passed (40%)**: Measures compilation and execution success

### Score Interpretation

| Score Range | Quality | Description |
|-------------|---------|-------------|
| 0.0 - 0.5 | Poor | Major issues with conversion |
| 0.5 - 0.8 | Good | Minor issues, generally acceptable |
| 0.8 - 1.0 | Excellent | High-quality conversion |

### Output Files

#### Converted Code Structure

```
batch_results/
├── converted/
│   ├── Clover_abs/
│   │   ├── Clover_abs.c          # Converted C code
│   │   └── test_Clover_abs.c     # Generated test file
│   └── another_file/
│       ├── another_file.c
│       └── test_another_file.c
├── reports/
│   ├── experiment_1_progress.json    # Detailed progress
│   ├── experiment_1_summary.csv      # Summary statistics
│   └── experiment_1_detailed_results.csv  # Per-file results
└── README.md                          # Batch documentation
```

#### Results CSV Format

```csv
Input_File,Status,Conversion_Score,Validation_Score,Test_Success,Error_Message,Start_Time,End_Time,Retry_Count,Notes
Clover_abs.dfy,completed,1.0,0.95,True,N/A,2025-07-22T15:00:00,2025-07-22T15:01:30,0,Successfully converted
```

## Troubleshooting

### Common Issues

#### 1. API Key Not Set

**Error**: `ValueError: API key is required`

**Solution**: Set environment variable or provide via prompt:
```bash
export DEEPSEEK_API_KEY="your_key"
```

#### 2. Compilation Failures

**Error**: `Compilation failed: undefined reference`

**Solution**: Check if the AI generated complete function definitions. The tool should copy the original function into the test file.

#### 3. Timeout Issues

**Error**: `Execution timeout after 100 seconds`

**Solution**: Increase timeout in configuration or check for infinite loops in generated code.

#### 4. Memory Issues

**Error**: `MemoryError` or slow performance

**Solution**: Process files in smaller batches:
```bash
python batch_convert.py --limit 5 --batch-name "small_batch"
```

### Debug Mode

Enable verbose logging:

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run with debug output
python batch_convert.py --limit 2 --batch-name "debug_test"
```

### Performance Optimization

1. **Use DeepSeek**: Generally faster than Claude for this task
2. **Batch Size**: Start with 10-20 files, increase gradually
3. **Parallel Processing**: Currently single-threaded, but can be extended
4. **Caching**: Results are cached to avoid reprocessing

## Advanced Features

### Custom Validation Rules

Create custom validation logic by extending `HeuristicValidator`:

```python
class CustomValidator(HeuristicValidator):
    def _check_custom_rule(self, dafny_code: str, c_code: str) -> float:
        # Implement custom validation logic
        return score
```

### Custom Test Generation

Modify test generation prompts in `DeepSeekConverter._generate_test_cases()`:

```python
prompt = f"""Custom test generation prompt:
{c_code}
"""
```

### Integration with Other Tools

The tool generates standard C code that can be integrated with:

- **Frama-C**: For ACSL verification
- **CBMC**: For bounded model checking
- **KLEE**: For symbolic execution
- **Valgrind**: For memory analysis

## Best Practices

1. **Start Small**: Begin with 5-10 files to test configuration
2. **Monitor Progress**: Check batch progress regularly
3. **Backup Results**: Important results are automatically saved
4. **Validate Manually**: Review high-scoring conversions manually
5. **Iterate**: Use failed cases to improve prompts and validation

## Support

For additional help:

1. Check the [README.md](README.md) for basic information
2. Review this usage guide for detailed examples
3. Open an issue on GitHub for bugs or feature requests
4. Check the logs in `batch_results/reports/` for detailed error information 