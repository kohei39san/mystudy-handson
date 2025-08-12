#!/bin/bash

# OCI Cost Alert Configuration Validation Script

set -e

echo "=== OCI Cost Alert Configuration Validation ==="

# Check if required files exist
echo "Checking required files..."
required_files=("main.tf" "variables.tf" "outputs.tf" "terraform.tf" "README.md")

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✓ $file exists"
    else
        echo "✗ $file is missing"
        exit 1
    fi
done

# Validate Terraform syntax
echo "Validating Terraform syntax..."
if command -v terraform &> /dev/null; then
    terraform fmt -check=true -diff=true
    terraform validate
    echo "✓ Terraform syntax is valid"
else
    echo "⚠ Terraform not found, skipping syntax validation"
fi

# Check for required variables
echo "Checking required variables..."
required_vars=("compartment_id" "alert_email")

for var in "${required_vars[@]}"; do
    if grep -q "variable \"$var\"" variables.tf; then
        echo "✓ Variable $var is defined"
    else
        echo "✗ Variable $var is missing"
        exit 1
    fi
done

# Check for required resources
echo "Checking required resources..."
required_resources=("oci_budget_budget" "oci_budget_alert_rule" "oci_ons_notification_topic" "oci_ons_subscription")

for resource in "${required_resources[@]}"; do
    if grep -q "resource \"$resource\"" main.tf; then
        echo "✓ Resource $resource is defined"
    else
        echo "✗ Resource $resource is missing"
        exit 1
    fi
done

echo "=== All validations passed! ==="