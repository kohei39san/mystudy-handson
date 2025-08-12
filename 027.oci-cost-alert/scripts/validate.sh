#!/bin/bash
# Enhanced validation script for OCI Cost Alert Terraform configuration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== OCI Cost Alert Configuration Validation ==="
echo "Project Directory: $PROJECT_DIR"
echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Validation counter
VALIDATIONS_PASSED=0
VALIDATIONS_FAILED=0

# Validation function
run_validation() {
    local validation_name="$1"
    local validation_command="$2"
    
    echo "🔍 $validation_name..."
    
    if eval "$validation_command"; then
        echo "✅ $validation_name passed"
        ((VALIDATIONS_PASSED++))
    else
        echo "❌ $validation_name failed"
        ((VALIDATIONS_FAILED++))
    fi
    echo ""
}

# Check prerequisites
check_prerequisites() {
    if ! command -v terraform &> /dev/null; then
        echo "Terraform is not installed"
        return 1
    fi
    return 0
}

# Check required files
check_required_files() {
    local required_files=("terraform.tf" "variables.tf" "main.tf" "outputs.tf" "terraform.tfvars.example" "README.md")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "Missing required file: $file"
            return 1
        fi
    done
    return 0
}

# Check terraform.tfvars
check_tfvars() {
    if [ ! -f "terraform.tfvars" ]; then
        echo "terraform.tfvars not found. Please copy terraform.tfvars.example and configure it."
        echo "   cp terraform.tfvars.example terraform.tfvars"
        return 1
    fi
    return 0
}

# Validate Terraform syntax
validate_terraform_syntax() {
    terraform fmt -check=true -diff=true > /dev/null 2>&1
}

# Validate Terraform configuration
validate_terraform_config() {
    terraform init -backend=false > /dev/null 2>&1
    terraform validate > /dev/null 2>&1
}

# Check required variables
check_required_variables() {
    local required_vars=("compartment_id" "alert_email")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}\s*=" terraform.tfvars; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo "Missing required variables in terraform.tfvars:"
        for var in "${missing_vars[@]}"; do
            echo "   - $var"
        done
        return 1
    fi
    return 0
}

# Validate email format
validate_email_format() {
    local email=$(grep "^alert_email\s*=" terraform.tfvars | sed 's/.*=\s*"\([^"]*\)".*/\1/')
    if [[ ! "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        echo "Invalid email format: $email"
        return 1
    fi
    return 0
}

# Validate compartment OCID format
validate_compartment_ocid() {
    local compartment_id=$(grep "^compartment_id\s*=" terraform.tfvars | sed 's/.*=\s*"\([^"]*\)".*/\1/')
    if [[ ! "$compartment_id" =~ ^ocid1\.compartment\.oc1\.\. ]]; then
        echo "Invalid compartment OCID format: $compartment_id"
        echo "   Expected format: ocid1.compartment.oc1..<unique_id>"
        return 1
    fi
    return 0
}

# Validate budget amount
validate_budget_amount() {
    if grep -q "^budget_amount\s*=" terraform.tfvars; then
        local budget_amount=$(grep "^budget_amount\s*=" terraform.tfvars | sed 's/.*=\s*\([0-9]*\).*/\1/')
        if [[ ! "$budget_amount" =~ ^[0-9]+$ ]] || [ "$budget_amount" -le 0 ]; then
            echo "Invalid budget amount: $budget_amount (must be a positive integer)"
            return 1
        fi
    fi
    return 0
}

# Validate threshold percentage
validate_threshold_percentage() {
    if grep -q "^alert_threshold_percentage\s*=" terraform.tfvars; then
        local threshold=$(grep "^alert_threshold_percentage\s*=" terraform.tfvars | sed 's/.*=\s*\([0-9]*\).*/\1/')
        if [[ ! "$threshold" =~ ^[0-9]+$ ]] || [ "$threshold" -le 0 ] || [ "$threshold" -gt 100 ]; then
            echo "Invalid threshold percentage: $threshold (must be between 1 and 100)"
            return 1
        fi
    fi
    return 0
}

# Check resource dependencies
check_resource_dependencies() {
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

# Validate provider configuration
validate_provider_config() {
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

# Run unit tests if available
run_unit_tests() {
    if [ -f "tests/unit_test.sh" ]; then
        echo "Running unit tests..."
        bash tests/unit_test.sh
    else
        echo "Unit tests not found, skipping..."
        return 0
    fi
}

# Main validation execution
main() {
    echo "Starting comprehensive validation..."
    echo ""
    
    run_validation "Prerequisites Check" "check_prerequisites"
    run_validation "Required Files Check" "check_required_files"
    run_validation "Terraform Variables File Check" "check_tfvars"
    run_validation "Terraform Syntax Validation" "validate_terraform_syntax"
    run_validation "Terraform Configuration Validation" "validate_terraform_config"
    run_validation "Required Variables Check" "check_required_variables"
    run_validation "Email Format Validation" "validate_email_format"
    run_validation "Compartment OCID Validation" "validate_compartment_ocid"
    run_validation "Budget Amount Validation" "validate_budget_amount"
    run_validation "Threshold Percentage Validation" "validate_threshold_percentage"
    run_validation "Resource Dependencies Check" "check_resource_dependencies"
    run_validation "Provider Configuration Validation" "validate_provider_config"
    
    echo "=== Validation Summary ==="
    echo "Validations Passed: $VALIDATIONS_PASSED"
    echo "Validations Failed: $VALIDATIONS_FAILED"
    echo "Total Validations: $((VALIDATIONS_PASSED + VALIDATIONS_FAILED))"
    echo ""
    
    if [ $VALIDATIONS_FAILED -eq 0 ]; then
        echo "🎉 All validations passed!"
        echo ""
        echo "Next steps:"
        echo "1. Run 'terraform plan' to review the execution plan"
        echo "2. Run 'terraform apply' to create the resources"
        echo "3. Check your email for the ONS subscription confirmation"
        echo ""
        echo "Optional: Run unit tests with 'bash tests/unit_test.sh'"
        echo "Optional: Run integration tests with 'bash tests/integration_test.sh'"
        exit 0
    else
        echo "❌ Some validations failed!"
        echo "Please fix the issues above before proceeding."
        exit 1
    fi
}

# Run main function
main "$@"