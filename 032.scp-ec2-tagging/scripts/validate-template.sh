#!/bin/bash

# SCP EC2 Tagging Enforcement - Template Validation Script
# This script validates the CloudFormation template

set -e

# Configuration
TEMPLATE_FILE="../cfn/scp-ec2-tagging.yaml"
REGION="ap-northeast-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is installed and configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured or credentials are invalid."
        exit 1
    fi
}

# Function to check if template file exists
check_template_file() {
    if [ ! -f "$TEMPLATE_FILE" ]; then
        print_error "Template file not found: $TEMPLATE_FILE"
        exit 1
    fi
    
    print_success "Template file found: $TEMPLATE_FILE"
}

# Function to validate YAML syntax
validate_yaml_syntax() {
    print_status "Validating YAML syntax..."
    
    if command -v python3 &> /dev/null; then
        python3 -c "
import yaml
import sys
try:
    with open('$TEMPLATE_FILE', 'r') as f:
        yaml.safe_load(f)
    print('YAML syntax is valid')
except yaml.YAMLError as e:
    print(f'YAML syntax error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Error reading file: {e}')
    sys.exit(1)
"
        print_success "YAML syntax validation passed."
    else
        print_warning "Python3 not found. Skipping YAML syntax validation."
    fi
}

# Function to validate CloudFormation template
validate_cloudformation_template() {
    print_status "Validating CloudFormation template..."
    
    local validation_output
    validation_output=$(aws cloudformation validate-template \
        --template-body file://$TEMPLATE_FILE \
        --region $REGION 2>&1)
    
    if [ $? -eq 0 ]; then
        print_success "CloudFormation template validation passed."
        echo ""
        print_status "Template details:"
        echo "$validation_output" | jq '.' 2>/dev/null || echo "$validation_output"
    else
        print_error "CloudFormation template validation failed:"
        echo "$validation_output"
        exit 1
    fi
}

# Function to analyze template content
analyze_template_content() {
    print_status "Analyzing template content..."
    
    # Check for required sections
    if grep -q "AWSTemplateFormatVersion" "$TEMPLATE_FILE"; then
        print_success "✓ AWSTemplateFormatVersion found"
    else
        print_warning "⚠ AWSTemplateFormatVersion not found"
    fi
    
    if grep -q "Description" "$TEMPLATE_FILE"; then
        print_success "✓ Description found"
    else
        print_warning "⚠ Description not found"
    fi
    
    if grep -q "Parameters:" "$TEMPLATE_FILE"; then
        print_success "✓ Parameters section found"
    else
        print_warning "⚠ Parameters section not found"
    fi
    
    if grep -q "Resources:" "$TEMPLATE_FILE"; then
        print_success "✓ Resources section found"
    else
        print_error "✗ Resources section not found (required)"
        exit 1
    fi
    
    if grep -q "Outputs:" "$TEMPLATE_FILE"; then
        print_success "✓ Outputs section found"
    else
        print_warning "⚠ Outputs section not found"
    fi
    
    # Check for SCP-specific content
    if grep -q "AWS::Organizations::Policy" "$TEMPLATE_FILE"; then
        print_success "✓ Organizations Policy resource found"
    else
        print_error "✗ Organizations Policy resource not found"
        exit 1
    fi
    
    if grep -q "SERVICE_CONTROL_POLICY" "$TEMPLATE_FILE"; then
        print_success "✓ SERVICE_CONTROL_POLICY type found"
    else
        print_error "✗ SERVICE_CONTROL_POLICY type not found"
        exit 1
    fi
    
    if grep -q "ec2:RunInstances" "$TEMPLATE_FILE"; then
        print_success "✓ EC2 RunInstances action found in policy"
    else
        print_warning "⚠ EC2 RunInstances action not found in policy"
    fi
}

# Function to check for common issues
check_common_issues() {
    print_status "Checking for common issues..."
    
    # Check for hardcoded values that should be parameters
    if grep -q "ap-northeast-1" "$TEMPLATE_FILE"; then
        print_warning "⚠ Hardcoded region found. Consider using parameters or pseudo parameters."
    fi
    
    # Check for proper indentation (basic check)
    if grep -q $'\t' "$TEMPLATE_FILE"; then
        print_warning "⚠ Tab characters found. YAML should use spaces for indentation."
    fi
    
    # Check for trailing whitespace
    if grep -q ' $' "$TEMPLATE_FILE"; then
        print_warning "⚠ Trailing whitespace found in template."
    fi
    
    print_success "Common issues check completed."
}

# Function to display template summary
display_template_summary() {
    echo ""
    print_status "Template Summary:"
    echo "=================="
    
    local resource_count=$(grep -c "Type: AWS::" "$TEMPLATE_FILE" || echo "0")
    local parameter_count=$(grep -A 100 "Parameters:" "$TEMPLATE_FILE" | grep -c "Type:" || echo "0")
    local output_count=$(grep -A 100 "Outputs:" "$TEMPLATE_FILE" | grep -c "Description:" || echo "0")
    
    echo "Resources: $resource_count"
    echo "Parameters: $parameter_count"
    echo "Outputs: $output_count"
    echo ""
    
    print_status "Resources found:"
    grep "Type: AWS::" "$TEMPLATE_FILE" | sed 's/^[ \t]*/  - /' || echo "  None"
}

# Main execution
main() {
    echo "=========================================="
    echo "SCP EC2 Tagging Template Validation"
    echo "=========================================="
    echo ""
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Run validations
    check_aws_cli
    check_template_file
    validate_yaml_syntax
    validate_cloudformation_template
    analyze_template_content
    check_common_issues
    display_template_summary
    
    echo ""
    print_success "All validations completed successfully!"
    print_status "The template is ready for deployment."
}

# Run main function
main "$@"