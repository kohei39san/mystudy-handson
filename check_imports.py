#!/usr/bin/env python3

# Check if all imports work
try:
    import os
    print("✓ os imported")
    
    import re
    print("✓ re imported")
    
    import json
    print("✓ json imported")
    
    import yaml
    print("✓ yaml imported")
    
    import shutil
    print("✓ shutil imported")
    
    from datetime import datetime
    print("✓ datetime imported")
    
    from pathlib import Path
    print("✓ pathlib imported")
    
    from typing import List, Dict, Any, Optional
    print("✓ typing imported")
    
    print("\nAll imports successful!")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Other error: {e}")

# Test basic functionality
print("\nTesting basic functionality:")
workspace_path = '/workspace'
pattern = re.compile(r'^[0-9]{3}\..*$')

matching_dirs = []
for item in os.listdir(workspace_path):
    item_path = os.path.join(workspace_path, item)
    if os.path.isdir(item_path) and pattern.match(item):
        matching_dirs.append(item)

print(f"Found {len(matching_dirs)} matching directories")
print("First 5:", matching_dirs[:5])