#!/usr/bin/env python3

# Import and run the analysis
import sys
sys.path.append('/workspace')

from analyze_directories import main

if __name__ == "__main__":
    selected_directories = main()
    
    # Store the results for further processing
    print(f"\n=== SUMMARY ===")
    print(f"Selected {len(selected_directories)} directories for processing:")
    for i, analysis in enumerate(selected_directories, 1):
        print(f"{i}. {analysis['name']}")