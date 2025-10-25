#!/usr/bin/env python3

import os
import re
from datetime import datetime

# Simple test to identify directories
workspace_path = '/workspace'
pattern = re.compile(r'^[0-9]{3}\..*$')

print("Directories matching pattern [0-9][0-9][0-9].*:")
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
                'readable': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
        except OSError:
            continue

# Sort by modification time (oldest first)
directories.sort(key=lambda x: x['mtime'])

print(f"Found {len(directories)} directories:")
for i, d in enumerate(directories[:10], 1):  # Show first 10
    print(f"{i:2d}. {d['name']} - {d['readable']}")

print(f"\nThe 3 oldest directories are:")
for i, d in enumerate(directories[:3], 1):
    print(f"{i}. {d['name']} - {d['readable']}")