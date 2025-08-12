#!/bin/bash

# Unit tests for OCI Cost Alert Configuration

set -e

echo "=== OCI Cost Alert Unit Tests ==="

# Test 1: Verify all required files exist
test_required_files() {
    echo "Test 1: Checking required files..."
    local files=("main.tf" "variables.tf" "outputs.tf" "terraform.tf" "README.md" "terraform.tfvars.example")
    local missing_files=()
    
    for file in "${files[@]}"; do
        if [[ ! -f "$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -eq 0 ]]; then
        echo "✓ All required files exist"
        return 0
    else
        echo "✗ Missing files: ${missing_files[*]}"
        return 1
    fi
}

# Test 2: Verify required variables are defined
test_required_variables() {
    echo "Test 2: Checking required variables..."
    local required_vars=("compartment_id" "alert_email" "budget_amount" "region")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "variable \"$var\"" variables.tf; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -eq 0 ]]; then
        echo "✓ All required variables are defined"
        return 0
    else
        echo "✗ Missing variables: ${missing_vars[*]}"
        return 1
    fi
}

# Test 3: Verify required resources are defined
test_required_resources() {
    echo "Test 3: Checking required resources..."
    local required_resources=("oci_budget_budget" "oci_budget_alert_rule" "oci_ons_notification_topic" "oci_ons_subscription")
    local missing_resources=()
    
    for resource in "${required_resources[@]}"; do
        if ! grep -q "resource \"$resource\"" main.tf; then
            missing_resources+=("$resource")
        fi
    done
    
    if [[ ${#missing_resources[@]} -eq 0 ]]; then
        echo "✓ All required resources are defined"
        return 0
    else
        echo "✗ Missing resources: ${missing_resources[*]}"
        return 1
    fi
}

# Test 4: Verify outputs are defined
test_outputs() {
    echo "Test 4: Checking outputs..."
    local required_outputs=("budget_id" "notification_topic_id" "alert_rules")
    local missing_outputs=()
    
    for output in "${required_outputs[@]}"; do
        if ! grep -q "output \"$output\"" outputs.tf; then
            missing_outputs+=("$output")
        fi
    done
    
    if [[ ${#missing_outputs[@]} -eq 0 ]]; then
        echo "✓ All required outputs are defined"
        return 0
    else
        echo "✗ Missing outputs: ${missing_outputs[*]}"
        return 1
    fi
}

# Test 5: Verify provider configuration
test_provider_config() {
    echo "Test 5: Checking provider configuration..."
    
    if grep -q "provider \"oci\"" terraform.tf; then
        echo "✓ OCI provider is configured"
        return 0
    else
        echo "✗ OCI provider is not configured"
        return 1
    fi
}

# Test 6: Verify README exists and has content
test_readme() {
    echo "Test 6: Checking README..."
    
    if [[ -f "README.md" ]] && [[ -s "README.md" ]]; then
        if grep -q "OCI" README.md && grep -q "コスト" README.md; then
            echo "✓ README.md exists and contains relevant content"
            return 0
        else
            echo "✗ README.md exists but lacks relevant content"
            return 1
        fi
    else
        echo "✗ README.md is missing or empty"
        return 1
    fi
}

# Run all tests
run_tests() {
    local failed_tests=0
    
    test_required_files || ((failed_tests++))
    test_required_variables || ((failed_tests++))
    test_required_resources || ((failed_tests++))
    test_outputs || ((failed_tests++))
    test_provider_config || ((failed_tests++))
    test_readme || ((failed_tests++))
    
    echo ""
    if [[ $failed_tests -eq 0 ]]; then
        echo "=== All tests passed! ==="
        return 0
    else
        echo "=== $failed_tests test(s) failed ==="
        return 1
    fi
}

# Change to the directory containing the Terraform files
cd "$(dirname "$0")/.."

# Run the tests
run_tests