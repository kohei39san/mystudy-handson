#!/bin/bash
# Script to analyze all directories and categorize them by infrastructure type

echo "=== Repository Infrastructure Analysis ==="
echo ""

for dir in */; do
    if [[ $dir =~ ^[0-9]{3}\. ]]; then
        echo "Directory: $dir"
        
        # Check for Terraform files
        tf_files=$(find "$dir" -name "*.tf" 2>/dev/null | wc -l)
        
        # Check for CloudFormation files
        cfn_files=$(find "$dir" -name "template.yaml" -o -name "*.yml" -o -name "*.json" 2>/dev/null | grep -v node_modules | wc -l)
        
        # Check for existing README
        readme_exists=$([ -f "$dir/README.md" ] && echo "YES" || echo "NO")
        
        # Check for existing architecture diagram
        diagram_exists=$([ -f "$dir/src/architecture.drawio" ] && echo "YES" || echo "NO")
        
        echo "  Terraform files: $tf_files"
        echo "  CloudFormation files: $cfn_files"
        echo "  README.md exists: $readme_exists"
        echo "  Architecture diagram exists: $diagram_exists"
        
        if [ $tf_files -gt 0 ] || [ $cfn_files -gt 0 ]; then
            echo "  STATUS: HAS INFRASTRUCTURE"
        else
            echo "  STATUS: NO INFRASTRUCTURE"
        fi
        echo ""
    fi
done