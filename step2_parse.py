#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/workspace')

from readme_updater import DirectoryAnalyzer, TerraformParser

# Test Terraform parsing
analyzer = DirectoryAnalyzer()
tf_parser = TerraformParser()

print("=== Step 2: Terraform Parsing ===")
all_directories = analyzer.find_matching_directories()
oldest_directories = analyzer.select_oldest_directories(all_directories, 3)

for i, dir_info in enumerate(oldest_directories, 1):
    analysis = analyzer.analyze_directory_structure(dir_info)
    print(f"\n{i}. Parsing {analysis['name']}")
    
    if analysis['terraform_files']:
        resources = tf_parser.parse_terraform_files(analysis['terraform_files'])
        
        total_resources = sum(len(resource_list) for resource_list in resources.values() if resource_list)
        print(f"   Found {total_resources} AWS resources:")
        
        for resource_type, resource_list in resources.items():
            if resource_list:
                print(f"   - {resource_type}: {len(resource_list)}")
                for resource in resource_list:
                    print(f"     * {resource['name']} (from {os.path.basename(resource['file'])})")
    else:
        print(f"   No Terraform files found")