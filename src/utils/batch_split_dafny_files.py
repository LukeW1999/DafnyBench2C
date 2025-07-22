#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量Dafny文件分割脚本
将目录中的所有Dafny文件分成两个版本：
1. 去掉requires和ensures的版本（保持空行维持相对位置）
2. 只包含requires和ensures的版本（标注原行号）
"""

import os
import re
import sys
from pathlib import Path
from .split_dafny_file import process_dafny_file

def batch_process_dafny_files(input_dir, output_dir):
    """
    批量处理目录中的所有Dafny文件
    
    Args:
        input_dir: 输入目录路径
        output_dir: 输出目录路径
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"错误: 输入目录不存在: {input_dir}")
        return
    
    # 查找所有.dfy文件
    dfy_files = list(input_path.glob("*.dfy"))
    
    if not dfy_files:
        print(f"在目录 {input_dir} 中没有找到.dfy文件")
        return
    
    print(f"找到 {len(dfy_files)} 个Dafny文件")
    
    # 处理每个文件
    for i, dfy_file in enumerate(dfy_files, 1):
        print(f"\n处理文件 {i}/{len(dfy_files)}: {dfy_file.name}")
        try:
            process_dafny_file(str(dfy_file), output_dir)
        except Exception as e:
            print(f"处理文件 {dfy_file.name} 时出错: {e}")
    
    print(f"\n批量处理完成！共处理了 {len(dfy_files)} 个文件")
    print(f"输出目录: {output_dir}")

def main():
    if len(sys.argv) != 3:
        print("用法: python batch_split_dafny_files.py <输入目录> <输出目录>")
        print("示例: python batch_split_dafny_files.py DafnyBench/dataset/hints_removed ./batch_output")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    try:
        batch_process_dafny_files(input_dir, output_dir)
    except Exception as e:
        print(f"批量处理过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 