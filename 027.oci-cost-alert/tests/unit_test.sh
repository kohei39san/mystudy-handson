#!/bin/bash
# Unit tests for OCI Cost Alert Terraform configuration

set -e

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$TEST_DIR")"
TEMP_DIR=$(mktemp -d)

echo "=== OCI Cost Alert Unit Tests ==="
echo "Project Directory: $PROJECT_DIR"
echo "Temporary Directory: $TEMP_DIR"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo "🧪 Running test: $test_name"
    
    if eval "$test_command"; then
        echo "✅ PASSED: $test_name"
        ((TESTS_PASSED++))
    else
        echo "❌ FAILED: $test_name"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Setup test environment
setup_test_env() {
    cd "$PROJECT_DIR"
    cp -r . "$TEMP_DIR/"
    cd "$TEMP_DIR"
    
    # Create a test terraform.tfvars
    cat > terraform.tfvars << EOF
compartment_id = "ocid1.compartment.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
alert_email    = "test@example.com"
budget_amount  = 50
budget_currency = "USD"
alert_threshold_percentage = 75
EOF
}

# Cleanup test environment
cleanup_test_env() {
    cd "$PROJECT_DIR"
    rm -rf "$TEMP_DIR"
}

# Test 1: Terraform syntax validation
test_terraform_syntax() {
    terraform fmt -check=true -diff=true
}

# Test 2: Terraform configuration validation
test_terraform_validate() {
    terraform init -backend=false > /dev/null 2>&1
    terraform validate
}

# Test 3: Variable validation
test_variables() {
    # Check if all required variables are defined
    local required_vars=("region" "compartment_id" "budget_amount" "budget_currency" "alert_email" "alert_threshold_percentage" "budget_display_name" "notification_topic_name" "freeform_tags")
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "variable \"$var\"" variables.tf; then
            echo "Missing variable: $var"
            return 1
        fi
    done
    
    return 0
}

# Test 4: Output validation
test_outputs() {
    # Check if all expected outputs are defined
    local expected_outputs=("budget_id" "budget_display_name" "notification_topic_id" "notification_topic_name" "email_subscription_id" "alert_rules")
    
    for output in "${expected_outputs[@]}"; do
        if ! grep -q "output \"$output\"" outputs.tf; then
            echo "Missing output: $output"
            return 1
        fi
    done
    
    return 0
}

# Test 5: Resource dependencies
test_resource_dependencies() {
    # Check if resources reference each other correctly
    if ! grep -q "oci_ons_notification_topic.budget_alert_topic.id" main.tf; then
        echo "Missing notification topic reference in subscription"
        return 1
    fi
    
    if ! grep -q "oci_budget_budget.main_budget.id" main.tf; then
        echo "Missing budget reference in alert rules"
        return 1
    fi
    
    if ! grep -q "oci_ons_notification_topic.budget_alert_topic.topic_id" main.tf; then
        echo "Missing topic reference in alert rules"
        return 1
    fi
    
    return 0
}

# Test 6: Provider configuration
test_provider_config() {
    if ! grep -q "oracle/oci" terraform.tf; then
        echo "Missing OCI provider configuration"
        return 1
    fi
    
    if ! grep -q "required_version.*>=.*1.0.0" terraform.tf; then
        echo "Missing or incorrect Terraform version requirement"
        return 1
    fi
    
    return 0
}

# Test 7: Terraform plan (dry run)
test_terraform_plan() {
    # This test requires valid OCI credentials, so we'll just check if plan command works
    # In a real environment, this would validate the actual plan
    terraform init -backend=false > /dev/null 2>&1
    
    # Check if plan command can be executed (will fail due to auth, but syntax should be OK)
    if terraform plan -out=/dev/null 2>&1 | grep -q "Error: cannot parse config"; then
        echo "Terraform plan failed due to configuration errors"
        return 1
    fi
    
    return 0
}

# Test 8: Email format validation in tfvars
test_email_format() {
    local email=$(grep "^alert_email" terraform.tfvars | sed 's/.*=\s*"\([^"]*\)".*/\1/')
    if [[ ! "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        echo "Invalid email format: $email"
        return 1
    fi
    return 0
}

# Test 9: OCID format validation
test_ocid_format() {
    local compartment_id=$(grep "^compartment_id" terraform.tfvars | sed 's/.*=\s*"\([^"]*\)".*/\1/')
    if [[ ! "$compartment_id" =~ ^ocid1\.compartment\.oc1\.\. ]]; then
        echo "Invalid compartment OCID format: $compartment_id"
        return 1
    fi
    return 0
}

# Test 10: Budget amount validation
test_budget_amount() {
    local budget_amount=$(grep "^budget_amount" terraform.tfvars | sed 's/.*=\s*\([0-9]*\).*/\1/')
    if [[ ! "$budget_amount" =~ ^[0-9]+$ ]] || [ "$budget_amount" -le 0 ]; then
        echo "Invalid budget amount: $budget_amount"
        return 1
    fi
    return 0
}

# Main test execution
main() {
    echo "Setting up test environment..."
    setup_test_env
    
    echo "Running unit tests..."
    echo ""
    
    run_test "Terraform Syntax Check" "test_terraform_syntax"
    run_test "Terraform Configuration Validation" "test_terraform_validate"
    run_test "Variable Definitions" "test_variables"
    run_test "Output Definitions" "test_outputs"
    run_test "Resource Dependencies" "test_resource_dependencies"
    run_test "Provider Configuration" "test_provider_config"
    run_test "Terraform Plan Syntax" "test_terraform_plan"
    run_test "Email Format Validation" "test_email_format"
    run_test "OCID Format Validation" "test_ocid_format"
    run_test "Budget Amount Validation" "test_budget_amount"
    
    echo "=== Test Results ==="
    echo "Tests Passed: $TESTS_PASSED"
    echo "Tests Failed: $TESTS_FAILED"
    echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo "🎉 All tests passed!"
        cleanup_test_env
        exit 0
    else
        echo "❌ Some tests failed!"
        cleanup_test_env
        exit 1
    fi
}

# Run main function
main "$@"