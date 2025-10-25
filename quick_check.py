#!/usr/bin/env python3

import os
import re
from datetime import datetime

def quick_check():
    workspace_path = '/workspace'
    pattern = re.compile(r'^[0-9]{3}\..*$')
    
    directories = []
    for item in os.listdir(workspace_path):
        item_path = os.path.join(workspace_path, item)
        if os.path.isdir(item_path) and pattern.match(item):
            try:
                stat_info = os.stat(item_path)
                mtime = stat_info.st_mtime
                directories.append({
                    'name': item,
                    'mtime': mtime,
                    'mtime_readable': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
            except OSError:
                continue
    
    # Sort by modification time (oldest first)
    directories.sort(key=lambda x: x['mtime'])
    
    print("All directories (oldest first):")
    for i, d in enumerate(directories, 1):
        print(f"{i:2d}. {d['name']} - {d['mtime_readable']}")
    
    print(f"\nThe 3 oldest directories are:")
    for i, d in enumerate(directories[:3], 1):
        print(f"{i}. {d['name']} - {d['mtime_readable']}")
        
        # Check what files are in each directory
        dir_path = os.path.join(workspace_path, d['name'])
        try:
            files = os.listdir(dir_path)
            tf_files = [f for f in files if f.endswith('.tf')]
            has_readme = 'README.md' in files
            has_src = 'src' in files
            
            print(f"   - README.md: {has_readme}")
            print(f"   - Terraform files: {len(tf_files)} ({', '.join(tf_files[:3])}{'...' if len(tf_files) > 3 else ''})")
            print(f"   - src directory: {has_src}")
        except OSError:
            print(f"   - Error reading directory")
    
    return directories[:3]

if __name__ == "__main__":
    oldest_three = quick_check()