#!/usr/bin/env python3

# Test the readme_updater script
import sys
import os
sys.path.append('/workspace')

# Import the main processor
from readme_updater import MainProcessor

def test_run():
    """Test run of the README updater."""
    try:
        processor = MainProcessor()
        processor.run()
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_run()