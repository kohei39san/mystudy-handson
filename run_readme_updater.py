#!/usr/bin/env python3

import sys
import os

# Add the workspace to Python path
sys.path.insert(0, '/workspace')

# Import and run the main function
try:
    from readme_updater import main
    print("Starting README updater...")
    main()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()