#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dafny文件分割脚本
将Dafny文件分成两个版本：
1. 去掉requires和ensures的版本（保持空行维持相对位置）
2. 只包含requires和ensures的版本（标注原行号）
"""

import os
import re
import sys
from pathlib import Path

def process_dafny_file(input_file_path, output_dir):
    """
    处理Dafny文件，生成两个版本
    
    Args:
        input_file_path: 输入的Dafny文件路径
        output_dir: 输出目录
    """
    # 创建输出目录
    code_only_dir = Path(output_dir) / "code_only"
    specs_only_dir = Path(output_dir) / "specs_only"
    
    code_only_dir.mkdir(parents=True, exist_ok=True)
    specs_only_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取输入文件
    with open(input_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 准备输出内容
    code_only_lines = []
    specs_only_lines = []
    
    # 处理每一行
    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()
        
        # 检查是否是requires或ensures行
        if stripped_line.startswith('requires '):
            # 添加到specs_only文件，标注行号
            specs_only_lines.append(f"{stripped_line} // Original line number: {line_num}\n")
            # 在code_only文件中添加TODO注释
            code_only_lines.append('  // TODO: add requires clauses\n')
        elif stripped_line.startswith('ensures '):
            # 添加到specs_only文件，标注行号
            specs_only_lines.append(f"{stripped_line} // Original line number: {line_num}\n")
            # 在code_only文件中添加TODO注释
            code_only_lines.append('  // TODO: add ensures clause\n')
        else:
            # 普通代码行，直接添加到code_only文件
            code_only_lines.append(line)
    
    # 生成输出文件名
    input_filename = Path(input_file_path).name
    base_name = input_filename.replace('.dfy', '')
    
    code_only_file = code_only_dir / f"{base_name}_code_only.dfy"
    specs_only_file = specs_only_dir / f"{base_name}_specs_only.txt"
    
    # 写入文件
    with open(code_only_file, 'w', encoding='utf-8') as f:
        f.writelines(code_only_lines)
    
    with open(specs_only_file, 'w', encoding='utf-8') as f:
        f.writelines(specs_only_lines)
    
    print(f"Processing complete: {input_filename}")
    print(f"  Code version: {code_only_file}")
    print(f"  Specification version: {specs_only_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python split_dafny_file.py <input_file_path> <output_directory>")
        print("Example: python split_dafny_file.py DafnyBench/DafnyBench/dataset/hints_removed/630-dafny_tmp_tmpz2kokaiq_Solution_no_hints.dfy ./output")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file does not exist: {input_file}")
        sys.exit(1)
    
    try:
        process_dafny_file(input_file, output_dir)
        print("Processing successful!")
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 