#!/bin/bash
# Directory inventory script to identify infrastructure directories and their current state

echo "=== DIRECTORY INVENTORY ==="
echo "Directory | Infrastructure Type | Has README | Has Diagram | Status"
echo "---------|-------------------|-----------|-------------|-------"

for dir in */; do
    if [[ $dir =~ ^[0-9]{3}\. ]]; then
        dir_name=${dir%/}
        
        # Check for infrastructure files
        tf_files=$(find "$dir" -name "*.tf" 2>/dev/null | wc -l)
        cfn_files=$(find "$dir" -name "*.yaml" -o -name "*.yml" -o -name "*.json" 2>/dev/null | grep -v terraform.tfvars | wc -l)
        
        # Determine infrastructure type
        infra_type="None"
        if [ $tf_files -gt 0 ]; then
            # Check if it's OCI or AWS Terraform
            if grep -r "oci_" "$dir"/*.tf 2>/dev/null >/dev/null; then
                infra_type="OCI-Terraform"
            else
                infra_type="AWS-Terraform"
            fi
        elif [ $cfn_files -gt 0 ]; then
            infra_type="CloudFormation"
        fi
        
        # Check for README and diagram
        has_readme="No"
        has_diagram="No"
        
        if [ -f "$dir/README.md" ]; then
            has_readme="Yes"
        fi
        
        if [ -f "$dir/src/architecture.drawio" ] || [ -f "$dir/src/architecture.svg" ]; then
            has_diagram="Yes"
        fi
        
        # Determine status
        status="OK"
        if [ "$infra_type" != "None" ] && [ "$has_readme" = "No" ]; then
            status="MISSING_README"
        elif [ "$infra_type" != "None" ] && [ "$has_diagram" = "No" ]; then
            status="MISSING_DIAGRAM"
        elif [ "$infra_type" = "None" ]; then
            status="NO_INFRA"
        fi
        
        echo "$dir_name | $infra_type | $has_readme | $has_diagram | $status"
    fi
done