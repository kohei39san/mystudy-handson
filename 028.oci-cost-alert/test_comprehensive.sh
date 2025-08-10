#!/bin/bash

# Comprehensive test suite for OCI Cost Alert Terraform configuration
# This script performs thorough validation of the Terraform configuration

set -e

echo "=== OCI Cost Alert Comprehensive Test Suite ==="

# Change to the directory containing the Terraform files
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to print colored output
print_test_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
    ((TOTAL_TESTS++))
}

print_failure() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
    ((TOTAL_TESTS++))
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    if eval "$test_command" &>/dev/null; then
        print_success "$test_name"
        return 0
    else
        print_failure "$test_name"
        return 1
    fi
}

print_test_header "File Structure Tests"

# Test 1: Check required files exist
required_files=(
    "terraform.tf"
    "variables.tf" 
    "budget.tf"
    "notification.tf"
    "outputs.tf"
    "README.md"
    "terraform.tfvars.example"
    "DEPLOYMENT_GUIDE.md"
    "deploy.sh"
    "destroy.sh"
    "test_validation.sh"
    ".gitignore"
)

for file in "${required_files[@]}"; do
    run_test "File $file exists" "test -f $file"
done

print_test_header "Terraform Configuration Tests"

# Test 2: Terraform formatting
run_test "Terraform files are properly formatted" "terraform fmt -check -diff"

# Test 3: Terraform initialization
run_test "Terraform initialization succeeds" "terraform init -backend=false"

# Test 4: Terraform validation
run_test "Terraform configuration is valid" "terraform validate"

print_test_header "Variable Definition Tests"

# Test 5: Required variables are defined
required_variables=(
    "region"
    "compartment_id"
    "budget_amount"
    "budget_reset_period"
    "alert_threshold_percentage"
    "alert_email_addresses"
    "budget_display_name"
    "notification_topic_name"
    "freeform_tags"
)

for var in "${required_variables[@]}"; do
    run_test "Variable '$var' is defined" "grep -q 'variable \"$var\"' variables.tf"
done

print_test_header "Resource Definition Tests"

# Test 6: Required resources are defined
required_resources=(
    "oci_budget_budget"
    "oci_budget_alert_rule"
    "oci_ons_notification_topic"
    "oci_ons_subscription"
)

for resource in "${required_resources[@]}"; do
    run_test "Resource '$resource' is defined" "grep -q 'resource \"$resource\"' *.tf"
done

print_test_header "Output Definition Tests"

# Test 7: Important outputs are defined
required_outputs=(
    "budget_id"
    "budget_display_name"
    "budget_amount"
    "alert_rule_id"
    "alert_threshold_percentage"
    "notification_topic_id"
    "notification_topic_name"
    "email_subscription_ids"
    "alert_email_addresses"
)

for output in "${required_outputs[@]}"; do
    run_test "Output '$output' is defined" "grep -q 'output \"$output\"' outputs.tf"
done

print_test_header "Configuration Quality Tests"

# Test 8: Provider configuration
run_test "OCI provider is configured" "grep -q 'provider \"oci\"' terraform.tf"
run_test "OCI provider version is specified" "grep -q 'version.*oci' terraform.tf"

# Test 9: Variable defaults
run_test "Region default is ap-osaka-1" "grep -A 3 'variable \"region\"' variables.tf | grep -q 'ap-osaka-1'"
run_test "Budget amount has default" "grep -A 5 'variable \"budget_amount\"' variables.tf | grep -q 'default'"

# Test 10: Resource relationships
run_test "Budget alert rule references budget" "grep -q 'oci_budget_budget.main_budget.id' budget.tf"
run_test "Email subscription references topic" "grep -q 'oci_ons_notification_topic.budget_alert_topic.id' notification.tf"

print_test_header "Documentation Tests"

# Test 11: README content
run_test "README contains Japanese content" "grep -q '概要' README.md"
run_test "README contains usage instructions" "grep -q '使用方法' README.md"
run_test "README contains file structure" "grep -q 'ファイル構成' README.md"

# Test 12: Example configuration
run_test "Example tfvars contains compartment_id" "grep -q 'compartment_id' terraform.tfvars.example"
run_test "Example tfvars contains email addresses" "grep -q 'alert_email_addresses' terraform.tfvars.example"

print_test_header "Script Tests"

# Test 13: Shell scripts
run_test "Deploy script is executable" "test -x deploy.sh"
run_test "Destroy script is executable" "test -x destroy.sh"
run_test "Test script is executable" "test -x test_validation.sh"

# Test 14: Script content
run_test "Deploy script contains validation" "grep -q 'terraform.tfvars' deploy.sh"
run_test "Destroy script contains safety checks" "grep -q 'WARNING' destroy.sh"

print_test_header "Security Tests"

# Test 15: Gitignore configuration
run_test ".gitignore excludes tfstate files" "grep -q '*.tfstate' .gitignore"
run_test ".gitignore excludes terraform.tfvars" "grep -q 'terraform.tfvars' .gitignore"
run_test ".gitignore excludes .terraform directory" "grep -q '.terraform/' .gitignore"

print_test_header "OCI-Specific Tests"

# Test 16: OCI resource configuration
run_test "Budget resource has required fields" "grep -q 'compartment_id.*var.compartment_id' budget.tf"
run_test "Alert rule has threshold configuration" "grep -q 'threshold.*var.alert_threshold_percentage' budget.tf"
run_test "Notification topic has proper naming" "grep -q 'name.*var.notification_topic_name' notification.tf"

# Test 17: Region configuration
run_test "Region is configurable" "grep -q 'region.*var.region' terraform.tf"

print_test_header "Test Results Summary"

echo ""
echo "=== Test Results ==="
echo -e "Total Tests: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed! The OCI Cost Alert configuration is ready for deployment.${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ $TESTS_FAILED test(s) failed. Please review and fix the issues above.${NC}"
    exit 1
fi