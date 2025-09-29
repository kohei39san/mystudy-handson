#!/bin/bash

# Script to inventory all directories and their contents
echo "=== Repository Inventory ==="
echo "Directory | README.md | Infrastructure Files | Architecture Diagram"
echo "---------|-----------|---------------------|--------------------"

for dir in /workspace/[0-9][0-9][0-9].*; do
    if [ -d "$dir" ]; then
        dirname=$(basename "$dir")
        
        # Check for README.md
        readme_exists="No"
        if [ -f "$dir/README.md" ]; then
            readme_exists="Yes"
        fi
        
        # Check for infrastructure files
        infra_files=""
        tf_count=$(find "$dir" -name "*.tf" 2>/dev/null | wc -l)
        yaml_count=$(find "$dir" -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)
        json_count=$(find "$dir" -name "*.json" 2>/dev/null | wc -l)
        
        if [ $tf_count -gt 0 ]; then
            infra_files="${infra_files}TF($tf_count) "
        fi
        if [ $yaml_count -gt 0 ]; then
            infra_files="${infra_files}YAML($yaml_count) "
        fi
        if [ $json_count -gt 0 ]; then
            infra_files="${infra_files}JSON($json_count) "
        fi
        
        if [ -z "$infra_files" ]; then
            infra_files="None"
        fi
        
        # Check for architecture diagram
        diagram_exists="No"
        if [ -f "$dir/src/architecture.drawio" ]; then
            diagram_exists="Yes"
        fi
        
        echo "$dirname | $readme_exists | $infra_files | $diagram_exists"
    fi
done