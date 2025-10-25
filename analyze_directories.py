#!/usr/bin/env python3
"""
Script to analyze directories matching pattern [0-9][0-9][0-9].* and identify the 3 oldest ones.
"""

import os
import re
import stat
from datetime import datetime
from pathlib import Path

def get_directory_modification_time(directory_path):
    """Get the modification time of a directory."""
    try:
        stat_info = os.stat(directory_path)
        return stat_info.st_mtime
    except OSError:
        return 0

def find_matching_directories(workspace_path):
    """Find all directories matching the pattern [0-9][0-9][0-9].*"""
    pattern = re.compile(r'^[0-9]{3}\..*$')
    matching_dirs = []
    
    try:
        for item in os.listdir(workspace_path):
            item_path = os.path.join(workspace_path, item)
            if os.path.isdir(item_path) and pattern.match(item):
                mtime = get_directory_modification_time(item_path)
                matching_dirs.append({
                    'name': item,
                    'path': item_path,
                    'mtime': mtime,
                    'mtime_readable': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
    except OSError as e:
        print(f"Error reading workspace directory: {e}")
        return []
    
    return matching_dirs

def select_oldest_directories(directories, count=3):
    """Select the oldest directories by modification time."""
    # Sort by modification time (oldest first)
    sorted_dirs = sorted(directories, key=lambda x: x['mtime'])
    return sorted_dirs[:count]

def analyze_directory_structure(directory_info):
    """Analyze the structure of a directory to identify infrastructure files."""
    dir_path = directory_info['path']
    analysis = {
        'name': directory_info['name'],
        'path': dir_path,
        'mtime_readable': directory_info['mtime_readable'],
        'has_readme': False,
        'terraform_files': [],
        'cloudformation_files': [],
        'has_existing_diagram': False,
        'src_directory': None
    }
    
    try:
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            
            if item.lower() == 'readme.md':
                analysis['has_readme'] = True
            elif item.endswith('.tf'):
                analysis['terraform_files'].append(item)
            elif item.endswith(('.yaml', '.yml', '.json')) and not item.startswith('.'):
                # Check if it's likely a CloudFormation template
                analysis['cloudformation_files'].append(item)
            elif item == 'src' and os.path.isdir(item_path):
                analysis['src_directory'] = item_path
                # Check for existing diagram in src directory
                src_files = os.listdir(item_path)
                if 'architecture.drawio' in src_files:
                    analysis['has_existing_diagram'] = True
    
    except OSError as e:
        print(f"Error analyzing directory {dir_path}: {e}")
    
    return analysis

def main():
    workspace_path = '/workspace'
    
    print("=== Directory Analysis for README Update Task ===\n")
    
    # Find all matching directories
    print("1. Finding directories matching pattern [0-9][0-9][0-9].*...")
    matching_dirs = find_matching_directories(workspace_path)
    print(f"Found {len(matching_dirs)} matching directories\n")
    
    # Sort and display all directories with timestamps
    print("2. All matching directories (sorted by modification time):")
    sorted_dirs = sorted(matching_dirs, key=lambda x: x['mtime'])
    for i, dir_info in enumerate(sorted_dirs, 1):
        print(f"   {i:2d}. {dir_info['name']} - {dir_info['mtime_readable']}")
    print()
    
    # Select the 3 oldest directories
    print("3. Selecting 3 oldest directories for processing:")
    oldest_dirs = select_oldest_directories(matching_dirs, 3)
    
    selected_analyses = []
    for i, dir_info in enumerate(oldest_dirs, 1):
        print(f"   {i}. {dir_info['name']} - {dir_info['mtime_readable']}")
        analysis = analyze_directory_structure(dir_info)
        selected_analyses.append(analysis)
    print()
    
    # Detailed analysis of selected directories
    print("4. Detailed analysis of selected directories:")
    print("=" * 60)
    
    for analysis in selected_analyses:
        print(f"\nDirectory: {analysis['name']}")
        print(f"Path: {analysis['path']}")
        print(f"Last Modified: {analysis['mtime_readable']}")
        print(f"Has README.md: {analysis['has_readme']}")
        print(f"Terraform files: {len(analysis['terraform_files'])} files")
        if analysis['terraform_files']:
            for tf_file in analysis['terraform_files']:
                print(f"  - {tf_file}")
        print(f"CloudFormation files: {len(analysis['cloudformation_files'])} files")
        if analysis['cloudformation_files']:
            for cf_file in analysis['cloudformation_files']:
                print(f"  - {cf_file}")
        print(f"Has src directory: {analysis['src_directory'] is not None}")
        print(f"Has existing diagram: {analysis['has_existing_diagram']}")
        print("-" * 40)
    
    return selected_analyses

if __name__ == "__main__":
    selected_directories = main()