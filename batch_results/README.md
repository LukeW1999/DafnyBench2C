# Batch Conversion Results: test_batch_2_final

## 📁 Directory Structure

```
batch_results/
├── converted/           # 转换后的C代码文件
│   ├── file1/          # 每个Dafny文件对应一个目录
│   │   ├── main.c      # 转换后的C代码
│   │   └── test.c      # 生成的测试文件
│   └── file2/
│       ├── main.c
│       └── test.c
├── reports/            # 进度和结果报告
│   ├── test_batch_2_final_progress.json    # 详细进度（JSON格式）
│   ├── test_batch_2_final_summary.csv      # 进度摘要（CSV格式）
│   └── test_batch_2_final_detailed_results.csv  # 详细结果（CSV格式）
└── results/            # 其他结果文件
```

## 📊 Progress Summary

- **Total Files**: 2
- **Completed**: 2
- **Failed**: 0
- **Pending**: 0

## 🔍 How to Read Results

1. **converted/**: 每个子目录包含一个Dafny文件的转换结果
2. **reports/**: 包含进度跟踪和统计信息
3. **results/**: 其他相关结果文件

## 📈 Validation Scores

- **Conversion Score**: 转换是否成功 (1.0 = 成功, 0.0 = 失败)
- **Validation Score**: 转换质量评分 (0.0-1.0)
- **Test Success**: 测试是否通过 (True/False)

## 🚀 Resume Capability

如果批处理中断，可以重新运行相同的命令来继续处理剩余的文件。
系统会自动跳过已完成的文件。

Generated on: 2025-07-22 15:24:53
