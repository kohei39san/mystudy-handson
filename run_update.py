#!/usr/bin/env python3

import sys
import os

# Add workspace to path
sys.path.insert(0, '/workspace')

# Import and run
try:
    print("Starting README updater...")
    
    # Import the classes
    from readme_updater import DirectoryAnalyzer, TerraformParser, DiagramGenerator, ReadmeUpdater
    
    # Initialize components
    analyzer = DirectoryAnalyzer()
    tf_parser = TerraformParser()
    diagram_generator = DiagramGenerator()
    readme_updater = ReadmeUpdater()
    
    print("=== README Update and Infrastructure Diagram Creation ===\n")
    
    # Step 1: Find and select directories
    print("1. Finding directories matching pattern [0-9][0-9][0-9].*...")
    all_directories = analyzer.find_matching_directories()
    print(f"   Found {len(all_directories)} matching directories")
    
    oldest_directories = analyzer.select_oldest_directories(all_directories, 3)
    print(f"   Selected 3 oldest directories for processing:")
    for i, dir_info in enumerate(oldest_directories, 1):
        print(f"   {i}. {dir_info['name']} - {dir_info['mtime_readable']}")
    print()
    
    # Step 2: Process each selected directory
    for i, dir_info in enumerate(oldest_directories, 1):
        print(f"Processing directory {i}/3: {dir_info['name']}")
        print("-" * 50)
        
        # Analyze directory structure
        analysis = analyzer.analyze_directory_structure(dir_info)
        print(f"   Directory analysis:")
        print(f"   - Has README: {analysis['has_readme']}")
        print(f"   - Terraform files: {len(analysis['terraform_files'])}")
        print(f"   - CloudFormation files: {len(analysis['cloudformation_files'])}")
        print(f"   - Has existing diagram: {analysis['has_existing_diagram']}")
        
        # Parse infrastructure files
        resources = {}
        if analysis['terraform_files']:
            print(f"   Parsing Terraform files...")
            resources = tf_parser.parse_terraform_files(analysis['terraform_files'])
            
            # Print resource summary
            total_resources = sum(len(resource_list) for resource_list in resources.values() if resource_list)
            if total_resources > 0:
                print(f"   Found {total_resources} AWS resources:")
                for resource_type, resource_list in resources.items():
                    if resource_list:
                        print(f"     - {resource_type}: {len(resource_list)}")
            else:
                print(f"   No AWS resources found")
        
        # Generate diagram
        if analysis['src_directory']:
            diagram_path = os.path.join(analysis['src_directory'], 'architecture.drawio')
        else:
            # Create src directory if it doesn't exist
            src_dir = os.path.join(analysis['path'], 'src')
            os.makedirs(src_dir, exist_ok=True)
            diagram_path = os.path.join(src_dir, 'architecture.drawio')
        
        print(f"   Generating diagram: {diagram_path}")
        diagram_success = diagram_generator.generate_diagram(resources, diagram_path)
        
        # Update README
        print(f"   Updating README...")
        readme_success = readme_updater.update_readme(analysis, resources)
        
        if diagram_success and readme_success:
            print(f"   ✓ Successfully processed {dir_info['name']}")
        else:
            print(f"   ✗ Failed to process {dir_info['name']}")
        
        print()
    
    print("=== Processing Complete ===")
    print(f"Processed {len(oldest_directories)} directories")
    print("Note: SVG files will be generated automatically from DrawIO files by the system")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()