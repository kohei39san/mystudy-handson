#!/bin/bash
# Script to identify all infrastructure directories and their current diagram status

echo "=== Infrastructure Directory Analysis ==="
echo ""

for dir in */; do
    if [[ $dir =~ ^[0-9]{3}\. ]]; then
        echo "Directory: $dir"
        
        # Check for infrastructure files
        tf_files=$(find "$dir" -name "*.tf" 2>/dev/null | wc -l)
        cfn_files=$(find "$dir" -name "*.yaml" -o -name "*.yml" -o -name "*.json" 2>/dev/null | grep -v terraform.tfvars | wc -l)
        ansible_files=$(find "$dir" -name "*.yml" 2>/dev/null | grep -E "(playbook|ansible)" | wc -l)
        
        echo "  - Terraform files: $tf_files"
        echo "  - CloudFormation files: $cfn_files"
        echo "  - Ansible files: $ansible_files"
        
        # Check for existing diagrams
        if [ -d "$dir/src" ]; then
            if [ -f "$dir/src/architecture.drawio" ]; then
                echo "  - Architecture diagram: EXISTS"
            else
                echo "  - Architecture diagram: MISSING"
            fi
        else
            echo "  - src directory: MISSING"
            echo "  - Architecture diagram: MISSING"
        fi
        
        # Check README.md
        if [ -f "$dir/README.md" ]; then
            if grep -q "architecture.svg" "$dir/README.md"; then
                echo "  - README diagram reference: EXISTS"
            else
                echo "  - README diagram reference: MISSING"
            fi
        else
            echo "  - README.md: MISSING"
        fi
        
        echo ""
    fi
done