#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/workspace')

from readme_updater import DirectoryAnalyzer

# Test directory analysis
analyzer = DirectoryAnalyzer()

print("=== Step 1: Directory Analysis ===")
all_directories = analyzer.find_matching_directories()
print(f"Found {len(all_directories)} matching directories")

oldest_directories = analyzer.select_oldest_directories(all_directories, 3)
print(f"\nSelected 3 oldest directories:")
for i, dir_info in enumerate(oldest_directories, 1):
    print(f"{i}. {dir_info['name']} - {dir_info['mtime_readable']}")

print(f"\nDetailed analysis:")
for i, dir_info in enumerate(oldest_directories, 1):
    analysis = analyzer.analyze_directory_structure(dir_info)
    print(f"\n{i}. {analysis['name']}")
    print(f"   - Has README: {analysis['has_readme']}")
    print(f"   - Terraform files: {len(analysis['terraform_files'])}")
    print(f"   - Has src directory: {analysis['src_directory'] is not None}")
    print(f"   - Has existing diagram: {analysis['has_existing_diagram']}")
    
    if analysis['terraform_files']:
        print(f"   - TF files:")
        for tf_file in analysis['terraform_files']:
            print(f"     * {os.path.basename(tf_file)}")