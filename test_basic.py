#!/usr/bin/env python3

# Test basic directory analysis
import os
import re
from datetime import datetime

def test_directory_analysis():
    workspace_path = '/workspace'
    pattern = re.compile(r'^[0-9]{3}\..*$')
    
    print("=== Testing Directory Analysis ===")
    
    # Find matching directories
    matching_dirs = []
    for item in os.listdir(workspace_path):
        item_path = os.path.join(workspace_path, item)
        if os.path.isdir(item_path) and pattern.match(item):
            try:
                stat_info = os.stat(item_path)
                mtime = stat_info.st_mtime
                matching_dirs.append({
                    'name': item,
                    'path': item_path,
                    'mtime': mtime,
                    'mtime_readable': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
            except OSError:
                continue
    
    # Sort by modification time (oldest first)
    matching_dirs.sort(key=lambda x: x['mtime'])
    
    print(f"Found {len(matching_dirs)} directories matching pattern")
    print("\nAll directories (oldest first):")
    for i, d in enumerate(matching_dirs, 1):
        print(f"{i:2d}. {d['name']} - {d['mtime_readable']}")
    
    # Select 3 oldest
    oldest_three = matching_dirs[:3]
    print(f"\nSelected 3 oldest directories:")
    
    for i, dir_info in enumerate(oldest_three, 1):
        print(f"\n{i}. {dir_info['name']} - {dir_info['mtime_readable']}")
        
        # Analyze directory contents
        try:
            files = os.listdir(dir_info['path'])
            
            # Check for README
            has_readme = 'README.md' in files
            readme_path = os.path.join(dir_info['path'], 'README.md') if has_readme else None
            
            # Check for Terraform files
            tf_files = [f for f in files if f.endswith('.tf')]
            
            # Check for src directory
            has_src = 'src' in files and os.path.isdir(os.path.join(dir_info['path'], 'src'))
            
            # Check for existing diagram
            has_diagram = False
            if has_src:
                src_files = os.listdir(os.path.join(dir_info['path'], 'src'))
                has_diagram = 'architecture.drawio' in src_files
            
            print(f"   - README.md: {has_readme}")
            print(f"   - Terraform files: {len(tf_files)} files")
            if tf_files:
                for tf_file in tf_files:
                    print(f"     * {tf_file}")
            print(f"   - src directory: {has_src}")
            print(f"   - Existing diagram: {has_diagram}")
            
            # If has README, show first few lines
            if has_readme:
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:3]
                        print(f"   - README preview:")
                        for line in lines:
                            print(f"     {line.strip()}")
                except Exception as e:
                    print(f"   - Error reading README: {e}")
                    
        except OSError as e:
            print(f"   Error analyzing directory: {e}")
    
    return oldest_three

if __name__ == "__main__":
    result = test_directory_analysis()