#!/bin/bash

# Test script for OCI Cost Alert Terraform configuration
# This script validates the Terraform configuration

set -e

echo "=== OCI Cost Alert Terraform Validation Test ==="

# Change to the directory containing the Terraform files
cd "$(dirname "$0")"

echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la

echo ""
echo "=== Step 1: Terraform Format Check ==="
if terraform fmt -check -diff; then
    echo "✅ Terraform formatting is correct"
else
    echo "❌ Terraform formatting issues found"
    echo "Run 'terraform fmt' to fix formatting"
    exit 1
fi

echo ""
echo "=== Step 2: Terraform Validation ==="
# Initialize terraform (required for validation)
if terraform init -backend=false; then
    echo "✅ Terraform initialization successful"
else
    echo "❌ Terraform initialization failed"
    exit 1
fi

# Validate the configuration
if terraform validate; then
    echo "✅ Terraform configuration is valid"
else
    echo "❌ Terraform configuration validation failed"
    exit 1
fi

echo ""
echo "=== Step 3: Check Required Files ==="
required_files=("terraform.tf" "variables.tf" "budget.tf" "notification.tf" "outputs.tf" "README.md" "terraform.tfvars.example")

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing"
        exit 1
    fi
done

echo ""
echo "=== Step 4: Check Variable Definitions ==="
# Check if all required variables are defined
required_vars=("compartment_id" "alert_email_addresses")

for var in "${required_vars[@]}"; do
    if grep -q "variable \"$var\"" variables.tf; then
        echo "✅ Variable '$var' is defined"
    else
        echo "❌ Required variable '$var' is not defined"
        exit 1
    fi
done

echo ""
echo "=== Step 5: Check Resource Definitions ==="
# Check if all required resources are defined
required_resources=("oci_budget_budget" "oci_budget_alert_rule" "oci_ons_notification_topic" "oci_ons_subscription")

for resource in "${required_resources[@]}"; do
    if grep -q "resource \"$resource\"" *.tf; then
        echo "✅ Resource '$resource' is defined"
    else
        echo "❌ Required resource '$resource' is not defined"
        exit 1
    fi
done

echo ""
echo "=== Step 6: Check Output Definitions ==="
# Check if important outputs are defined
required_outputs=("budget_id" "alert_rule_id" "notification_topic_id")

for output in "${required_outputs[@]}"; do
    if grep -q "output \"$output\"" outputs.tf; then
        echo "✅ Output '$output' is defined"
    else
        echo "❌ Important output '$output' is not defined"
        exit 1
    fi
done

echo ""
echo "=== All Tests Passed! ==="
echo "✅ OCI Cost Alert Terraform configuration is ready for deployment"