#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch split Dafny files in a directory
"""

import os
import sys
from pathlib import Path
from .split_dafny_file import process_dafny_file

def main():
    if len(sys.argv) != 3:
        print("Usage: python batch_split_dafny_files.py <input_directory> <output_directory>")
        print("Example: python batch_split_dafny_files.py DafnyBench/DafnyBench/dataset/hints_removed ./batch_output")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all .dfy files
    dfy_files = list(input_dir.glob("*.dfy"))
    
    if not dfy_files:
        print(f"No .dfy files found in {input_dir}")
        sys.exit(1)
    
    print(f"Found {len(dfy_files)} Dafny files to process")
    
    # Process each file
    for i, dfy_file in enumerate(dfy_files, 1):
        print(f"\nProcessing file {i}/{len(dfy_files)}: {dfy_file.name}")
        
        try:
            # Create subdirectory for this file
            file_output_dir = output_dir / dfy_file.stem
            file_output_dir.mkdir(exist_ok=True)
            
            process_dafny_file(dfy_file, file_output_dir)
        except Exception as e:
            print(f"Error processing file {dfy_file.name}: {e}")
    
    print(f"\nBatch processing complete! Processed {len(dfy_files)} files")
    print(f"Results saved to: {output_dir}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error during batch processing: {e}")
        sys.exit(1) 