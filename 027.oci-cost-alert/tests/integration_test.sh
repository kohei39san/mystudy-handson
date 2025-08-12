#!/bin/bash
# Integration tests for OCI Cost Alert Terraform configuration
# These tests validate the complete workflow and resource interactions

set -e

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$TEST_DIR")"

echo "=== OCI Cost Alert Integration Tests ==="
echo "Project Directory: $PROJECT_DIR"
echo ""

# Test configuration
TEST_COMPARTMENT_ID="ocid1.compartment.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
TEST_EMAIL="integration-test@example.com"
TEST_BUDGET_AMOUNT=25
TEST_THRESHOLD=70

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_integration_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo "🔗 Running integration test: $test_name"
    
    if eval "$test_command"; then
        echo "✅ PASSED: $test_name"
        ((TESTS_PASSED++))
    else
        echo "❌ FAILED: $test_name"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Setup integration test environment
setup_integration_env() {
    cd "$PROJECT_DIR"
    
    # Create integration test terraform.tfvars
    cat > terraform.tfvars << EOF
compartment_id = "$TEST_COMPARTMENT_ID"
alert_email    = "$TEST_EMAIL"
budget_amount  = $TEST_BUDGET_AMOUNT
budget_currency = "USD"
alert_threshold_percentage = $TEST_THRESHOLD
budget_display_name = "Integration Test Budget"
notification_topic_name = "integration-test-topic"
freeform_tags = {
  Environment = "test"
  Terraform   = "true"
  TestType    = "integration"
}
EOF
}

# Cleanup integration test environment
cleanup_integration_env() {
    cd "$PROJECT_DIR"
    if [ -f "terraform.tfvars" ]; then
        rm terraform.tfvars
    fi
    if [ -f "terraform.tfplan" ]; then
        rm terraform.tfplan
    fi
}

# Test 1: Complete Terraform workflow (init, plan, validate)
test_complete_workflow() {
    # Initialize Terraform
    if ! terraform init -backend=false > /dev/null 2>&1; then
        echo "Terraform init failed"
        return 1
    fi
    
    # Validate configuration
    if ! terraform validate > /dev/null 2>&1; then
        echo "Terraform validate failed"
        return 1
    fi
    
    # Create plan (will fail due to auth, but should generate valid plan structure)
    terraform plan -out=terraform.tfplan > /dev/null 2>&1 || true
    
    # Check if plan file was created (indicates successful parsing)
    if [ ! -f "terraform.tfplan" ]; then
        echo "Terraform plan file not created - configuration may have syntax errors"
        return 1
    fi
    
    return 0
}

# Test 2: Resource count validation
test_resource_count() {
    # Count expected resources in the plan
    local expected_resources=("oci_budget_budget" "oci_budget_alert_rule" "oci_ons_notification_topic" "oci_ons_subscription")
    
    for resource in "${expected_resources[@]}"; do
        if ! grep -q "$resource" main.tf; then
            echo "Missing expected resource: $resource"
            return 1
        fi
    done
    
    # Check for correct number of alert rules (should be 3)
    local alert_rule_count=$(grep -c "resource \"oci_budget_alert_rule\"" main.tf)
    if [ "$alert_rule_count" -ne 3 ]; then
        echo "Expected 3 alert rules, found $alert_rule_count"
        return 1
    fi
    
    return 0
}

# Test 3: Variable interpolation
test_variable_interpolation() {
    # Check if variables are properly referenced in resources
    local var_references=("var.compartment_id" "var.alert_email" "var.budget_amount" "var.alert_threshold_percentage")
    
    for var_ref in "${var_references[@]}"; do
        if ! grep -q "$var_ref" main.tf; then
            echo "Missing variable reference: $var_ref"
            return 1
        fi
    done
    
    return 0
}

# Test 4: Output dependencies
test_output_dependencies() {
    # Check if outputs reference the correct resources
    local output_refs=("oci_budget_budget.main_budget.id" "oci_ons_notification_topic.budget_alert_topic.id" "oci_ons_subscription.budget_alert_email.id")
    
    for output_ref in "${output_refs[@]}"; do
        if ! grep -q "$output_ref" outputs.tf; then
            echo "Missing output reference: $output_ref"
            return 1
        fi
    done
    
    return 0
}

# Test 5: Tag consistency
test_tag_consistency() {
    # Check if freeform_tags are applied to all resources
    local tagged_resources=$(grep -c "freeform_tags.*=.*var.freeform_tags" main.tf)
    local total_resources=$(grep -c "^resource " main.tf)
    
    if [ "$tagged_resources" -ne "$total_resources" ]; then
        echo "Not all resources have freeform_tags applied. Tagged: $tagged_resources, Total: $total_resources"
        return 1
    fi
    
    return 0
}

# Test 6: Alert rule configuration
test_alert_rule_config() {
    # Check if alert rules have different thresholds
    if ! grep -q "threshold.*=.*var.alert_threshold_percentage" main.tf; then
        echo "Missing configurable threshold in alert rule"
        return 1
    fi
    
    if ! grep -q "threshold.*=.*100" main.tf; then
        echo "Missing 100% threshold alert rule"
        return 1
    fi
    
    # Check for different alert types
    if ! grep -q "type.*=.*\"ACTUAL\"" main.tf; then
        echo "Missing ACTUAL type alert rule"
        return 1
    fi
    
    if ! grep -q "type.*=.*\"FORECAST\"" main.tf; then
        echo "Missing FORECAST type alert rule"
        return 1
    fi
    
    return 0
}

# Test 7: Notification configuration
test_notification_config() {
    # Check if notification topic is properly configured
    if ! grep -q "protocol.*=.*\"EMAIL\"" main.tf; then
        echo "Missing EMAIL protocol in subscription"
        return 1
    fi
    
    if ! grep -q "endpoint.*=.*var.alert_email" main.tf; then
        echo "Missing email endpoint configuration"
        return 1
    fi
    
    # Check if alert rules reference the notification topic
    if ! grep -q "recipients.*=.*oci_ons_notification_topic.budget_alert_topic.topic_id" main.tf; then
        echo "Alert rules not properly linked to notification topic"
        return 1
    fi
    
    return 0
}

# Test 8: Budget configuration
test_budget_config() {
    # Check budget configuration
    if ! grep -q "reset_period.*=.*\"MONTHLY\"" main.tf; then
        echo "Missing monthly reset period"
        return 1
    fi
    
    if ! grep -q "amount.*=.*var.budget_amount" main.tf; then
        echo "Missing budget amount configuration"
        return 1
    fi
    
    if ! grep -q "targets.*=.*\[var.compartment_id\]" main.tf; then
        echo "Missing compartment target configuration"
        return 1
    fi
    
    return 0
}

# Test 9: Provider version constraints
test_provider_constraints() {
    # Check if provider version is properly constrained
    if ! grep -q "version.*=.*\"~>.*5.0\"" terraform.tf; then
        echo "Missing or incorrect OCI provider version constraint"
        return 1
    fi
    
    if ! grep -q "required_version.*>=.*1.0.0" terraform.tf; then
        echo "Missing or incorrect Terraform version constraint"
        return 1
    fi
    
    return 0
}

# Test 10: Configuration file validation
test_config_files() {
    # Check if all required files exist
    local required_files=("terraform.tf" "variables.tf" "main.tf" "outputs.tf" "terraform.tfvars.example" "README.md")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "Missing required file: $file"
            return 1
        fi
    done
    
    # Check if example file has proper format
    if ! grep -q "compartment_id.*=.*\"ocid1.compartment" terraform.tfvars.example; then
        echo "terraform.tfvars.example missing proper compartment_id example"
        return 1
    fi
    
    return 0
}

# Main integration test execution
main() {
    echo "Setting up integration test environment..."
    setup_integration_env
    
    echo "Running integration tests..."
    echo ""
    
    run_integration_test "Complete Terraform Workflow" "test_complete_workflow"
    run_integration_test "Resource Count Validation" "test_resource_count"
    run_integration_test "Variable Interpolation" "test_variable_interpolation"
    run_integration_test "Output Dependencies" "test_output_dependencies"
    run_integration_test "Tag Consistency" "test_tag_consistency"
    run_integration_test "Alert Rule Configuration" "test_alert_rule_config"
    run_integration_test "Notification Configuration" "test_notification_config"
    run_integration_test "Budget Configuration" "test_budget_config"
    run_integration_test "Provider Version Constraints" "test_provider_constraints"
    run_integration_test "Configuration Files" "test_config_files"
    
    echo "=== Integration Test Results ==="
    echo "Tests Passed: $TESTS_PASSED"
    echo "Tests Failed: $TESTS_FAILED"
    echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
    
    cleanup_integration_env
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo "🎉 All integration tests passed!"
        exit 0
    else
        echo "❌ Some integration tests failed!"
        exit 1
    fi
}

# Run main function
main "$@"