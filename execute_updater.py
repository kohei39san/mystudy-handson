#!/usr/bin/env python3

# Execute the README updater
import sys
import os

# Ensure we can import from the workspace
sys.path.insert(0, '/workspace')

def run_updater():
    try:
        # Import the main function
        from readme_updater import MainProcessor
        
        print("Initializing README updater...")
        processor = MainProcessor()
        
        print("Starting processing...")
        processor.run()
        
        print("Processing completed successfully!")
        
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_updater()