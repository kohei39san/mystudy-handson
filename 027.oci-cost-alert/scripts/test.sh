#!/bin/bash
# Comprehensive test runner for OCI Cost Alert Terraform configuration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== OCI Cost Alert Comprehensive Test Suite ==="
echo "Project Directory: $PROJECT_DIR"
echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test suite function
run_test_suite() {
    local suite_name="$1"
    local test_script="$2"
    
    echo "🧪 Running $suite_name..."
    echo "=================================================="
    
    if [ -f "$test_script" ] && [ -x "$test_script" ]; then
        if bash "$test_script"; then
            echo "✅ $suite_name: PASSED"
            ((PASSED_TESTS++))
        else
            echo "❌ $suite_name: FAILED"
            ((FAILED_TESTS++))
        fi
    else
        echo "⚠️  $suite_name: Test script not found or not executable: $test_script"
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
    echo ""
}

# Make scripts executable
make_scripts_executable() {
    echo "🔧 Making scripts executable..."
    
    local scripts=("scripts/validate.sh" "scripts/cleanup.sh" "tests/unit_test.sh" "tests/integration_test.sh")
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            chmod +x "$script"
            echo "   Made executable: $script"
        fi
    done
    echo ""
}

# Pre-test setup
pre_test_setup() {
    echo "🔧 Pre-test setup..."
    
    # Create test terraform.tfvars if it doesn't exist
    if [ ! -f "terraform.tfvars" ]; then
        echo "   Creating test terraform.tfvars..."
        cat > terraform.tfvars << EOF
# Test configuration - DO NOT USE IN PRODUCTION
compartment_id = "ocid1.compartment.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
alert_email    = "test@example.com"
budget_amount  = 50
budget_currency = "USD"
alert_threshold_percentage = 75
budget_display_name = "Test Budget Alert"
notification_topic_name = "test-budget-alert-topic"
freeform_tags = {
  Environment = "test"
  Terraform   = "true"
  TestRun     = "true"
}
EOF
        echo "   Test terraform.tfvars created"
    else
        echo "   terraform.tfvars already exists"
    fi
    echo ""
}

# Post-test cleanup
post_test_cleanup() {
    echo "🧹 Post-test cleanup..."
    
    # Remove test terraform.tfvars if it was created by this script
    if [ -f "terraform.tfvars" ] && grep -q "DO NOT USE IN PRODUCTION" terraform.tfvars; then
        rm terraform.tfvars
        echo "   Removed test terraform.tfvars"
    fi
    
    # Clean up any Terraform files
    if [ -f ".terraform.lock.hcl" ]; then
        rm .terraform.lock.hcl
        echo "   Removed .terraform.lock.hcl"
    fi
    
    if [ -d ".terraform" ]; then
        rm -rf .terraform
        echo "   Removed .terraform directory"
    fi
    
    if [ -f "terraform.tfplan" ]; then
        rm terraform.tfplan
        echo "   Removed terraform.tfplan"
    fi
    
    echo ""
}

# Display test summary
display_summary() {
    echo "=================================================="
    echo "=== Test Suite Summary ==="
    echo "Total Test Suites: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo "🎉 All test suites passed!"
        echo ""
        echo "Your OCI Cost Alert configuration is ready for deployment!"
        echo ""
        echo "Next steps:"
        echo "1. Configure your actual terraform.tfvars with real values"
        echo "2. Set up OCI authentication (CLI or environment variables)"
        echo "3. Run 'terraform plan' to review the execution plan"
        echo "4. Run 'terraform apply' to create the resources"
        echo "5. Confirm the email subscription in your inbox"
        return 0
    else
        echo "❌ Some test suites failed!"
        echo ""
        echo "Please review the failed tests above and fix any issues."
        echo "Run individual test suites for more detailed information:"
        echo "  - Validation: bash scripts/validate.sh"
        echo "  - Unit Tests: bash tests/unit_test.sh"
        echo "  - Integration Tests: bash tests/integration_test.sh"
        return 1
    fi
}

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verbose  Enable verbose output"
    echo "  --no-cleanup   Skip post-test cleanup"
    echo "  --unit-only    Run only unit tests"
    echo "  --integration-only  Run only integration tests"
    echo "  --validation-only   Run only validation tests"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all test suites"
    echo "  $0 --unit-only        # Run only unit tests"
    echo "  $0 --no-cleanup       # Run all tests but skip cleanup"
    echo ""
}

# Parse command line arguments
VERBOSE=false
NO_CLEANUP=false
UNIT_ONLY=false
INTEGRATION_ONLY=false
VALIDATION_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-cleanup)
            NO_CLEANUP=true
            shift
            ;;
        --unit-only)
            UNIT_ONLY=true
            shift
            ;;
        --integration-only)
            INTEGRATION_ONLY=true
            shift
            ;;
        --validation-only)
            VALIDATION_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main test execution
main() {
    echo "Starting comprehensive test suite..."
    echo ""
    
    # Setup
    make_scripts_executable
    pre_test_setup
    
    # Run test suites based on options
    if [ "$VALIDATION_ONLY" = true ]; then
        run_test_suite "Validation Tests" "scripts/validate.sh"
    elif [ "$UNIT_ONLY" = true ]; then
        run_test_suite "Unit Tests" "tests/unit_test.sh"
    elif [ "$INTEGRATION_ONLY" = true ]; then
        run_test_suite "Integration Tests" "tests/integration_test.sh"
    else
        # Run all test suites
        run_test_suite "Validation Tests" "scripts/validate.sh"
        run_test_suite "Unit Tests" "tests/unit_test.sh"
        run_test_suite "Integration Tests" "tests/integration_test.sh"
    fi
    
    # Cleanup
    if [ "$NO_CLEANUP" != true ]; then
        post_test_cleanup
    fi
    
    # Display results
    display_summary
    exit $?
}

# Run main function
main "$@"