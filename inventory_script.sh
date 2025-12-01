#!/bin/bash

# Script to inventory all directories and their infrastructure/documentation status
echo "Directory Inventory Report"
echo "========================="
echo ""

for dir in $(ls -d [0-9][0-9][0-9].* 2>/dev/null | sort); do
    if [ -d "$dir" ]; then
        echo "Directory: $dir"
        
        # Check for infrastructure files
        tf_files=$(find "$dir" -name "*.tf" 2>/dev/null | wc -l)
        yaml_files=$(find "$dir" -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)
        json_files=$(find "$dir" -name "*.json" 2>/dev/null | wc -l)
        
        echo "  Infrastructure files:"
        echo "    Terraform (.tf): $tf_files"
        echo "    YAML/YML: $yaml_files"
        echo "    JSON: $json_files"
        
        # Check for documentation
        if [ -f "$dir/README.md" ]; then
            echo "  README.md: ✓ Present"
            # Check if README references a diagram
            if grep -q "architecture.svg\|構成図\|Architecture Diagram" "$dir/README.md" 2>/dev/null; then
                echo "  Diagram reference in README: ✓ Present"
            else
                echo "  Diagram reference in README: ✗ Missing"
            fi
        else
            echo "  README.md: ✗ Missing"
        fi
        
        # Check for architecture diagram
        if [ -f "$dir/src/architecture.drawio" ]; then
            echo "  Architecture diagram: ✓ Present"
        else
            echo "  Architecture diagram: ✗ Missing"
        fi
        
        # Check for src directory
        if [ -d "$dir/src" ]; then
            echo "  src directory: ✓ Present"
        else
            echo "  src directory: ✗ Missing"
        fi
        
        echo ""
    fi
done