#!/bin/bash
# Inventory script to analyze all numbered directories

echo "=== Infrastructure Directory Inventory ==="
echo ""

for dir in [0-9][0-9][0-9].*; do
    if [ -d "$dir" ]; then
        echo "Directory: $dir"
        echo "  README.md: $([ -f "$dir/README.md" ] && echo "EXISTS" || echo "MISSING")"
        echo "  Terraform files: $(find "$dir" -name "*.tf" -type f | wc -l) files"
        echo "  CloudFormation templates: $(find "$dir" -name "*.yaml" -o -name "*.yml" -o -name "*.json" -type f | grep -v node_modules | wc -l) files"
        echo "  Architecture diagram: $([ -f "$dir/src/architecture.drawio" ] && echo "EXISTS" || echo "MISSING")"
        echo "  src directory: $([ -d "$dir/src" ] && echo "EXISTS" || echo "MISSING")"
        echo ""
    fi
done