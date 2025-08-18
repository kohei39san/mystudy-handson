#!/bin/bash

# Script to inventory all directories and their infrastructure code status
echo "=== Repository Infrastructure Inventory ==="
echo ""

for dir in $(ls -d [0-9][0-9][0-9].* 2>/dev/null | sort); do
    echo "Directory: $dir"
    
    # Check for README.md
    if [ -f "$dir/README.md" ]; then
        echo "  ✓ README.md exists"
        # Check if README references architecture diagram
        if grep -q "architecture.svg" "$dir/README.md"; then
            echo "  ✓ README references architecture diagram"
        else
            echo "  ✗ README does NOT reference architecture diagram"
        fi
    else
        echo "  ✗ README.md missing"
    fi
    
    # Check for src directory and architecture files
    if [ -d "$dir/src" ]; then
        echo "  ✓ src directory exists"
        if [ -f "$dir/src/architecture.drawio" ]; then
            echo "  ✓ architecture.drawio exists"
        else
            echo "  ✗ architecture.drawio missing"
        fi
        if [ -f "$dir/src/architecture.svg" ]; then
            echo "  ✓ architecture.svg exists"
        else
            echo "  ✗ architecture.svg missing"
        fi
    else
        echo "  ✗ src directory missing"
    fi
    
    # Check for infrastructure code
    tf_files=$(find "$dir" -name "*.tf" 2>/dev/null | wc -l)
    yaml_files=$(find "$dir" -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)
    json_files=$(find "$dir" -name "*.json" 2>/dev/null | grep -v package 2>/dev/null | wc -l)
    
    echo "  Infrastructure files:"
    echo "    Terraform files: $tf_files"
    echo "    YAML files: $yaml_files"
    echo "    JSON files: $json_files"
    
    if [ $tf_files -gt 0 ] || [ $yaml_files -gt 0 ] || [ $json_files -gt 0 ]; then
        echo "  ✓ Contains infrastructure code"
    else
        echo "  ✗ No infrastructure code found"
    fi
    
    echo ""
done