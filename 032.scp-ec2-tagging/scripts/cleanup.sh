#!/bin/bash

# SCP EC2 Tagging Enforcement - Cleanup Script
# This script removes the CloudFormation stack and associated SCP policy

set -e

# Configuration
STACK_NAME="scp-ec2-tagging-enforcement"
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

# Function to check if stack exists
stack_exists() {
    aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &> /dev/null
}

# Function to get policy ID from stack
get_policy_id() {
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`PolicyId`].OutputValue' \
        --output text 2>/dev/null || echo ""
}

# Function to check policy attachments
check_policy_attachments() {
    local policy_id=$1
    
    if [ -z "$policy_id" ]; then
        return 0
    fi
    
    print_status "Checking for policy attachments..."
    
    local attachments=$(aws organizations list-targets-for-policy \
        --policy-id $policy_id \
        --query 'Targets[*].TargetId' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$attachments" ] && [ "$attachments" != "None" ]; then
        print_warning "Policy is still attached to the following targets:"
        aws organizations list-targets-for-policy \
            --policy-id $policy_id \
            --query 'Targets[*].[TargetId,Name,Type]' \
            --output table 2>/dev/null || true
        echo ""
        print_warning "Please detach the policy from all targets before deletion."
        
        read -p "Do you want to automatically detach the policy from all targets? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            detach_policy_from_all_targets $policy_id
        else
            print_error "Cannot delete stack while policy is attached to targets."
            exit 1
        fi
    else
        print_success "Policy is not attached to any targets."
    fi
}

# Function to detach policy from all targets
detach_policy_from_all_targets() {
    local policy_id=$1
    
    print_status "Detaching policy from all targets..."
    
    local targets=$(aws organizations list-targets-for-policy \
        --policy-id $policy_id \
        --query 'Targets[*].TargetId' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$targets" ] && [ "$targets" != "None" ]; then
        for target in $targets; do
            print_status "Detaching policy from target: $target"
            aws organizations detach-policy \
                --policy-id $policy_id \
                --target-id $target
        done
        print_success "Policy detached from all targets."
    fi
}

# Function to delete stack
delete_stack() {
    if ! stack_exists; then
        print_warning "Stack $STACK_NAME does not exist."
        return 0
    fi
    
    # Get policy ID before deletion
    local policy_id=$(get_policy_id)
    
    # Check for policy attachments
    if [ -n "$policy_id" ]; then
        check_policy_attachments $policy_id
    fi
    
    print_status "Deleting CloudFormation stack: $STACK_NAME"
    
    aws cloudformation delete-stack \
        --stack-name $STACK_NAME \
        --region $REGION
    
    print_status "Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete \
        --stack-name $STACK_NAME \
        --region $REGION
    
    print_success "Stack deletion completed successfully."
}

# Function to confirm deletion
confirm_deletion() {
    echo ""
    print_warning "This will delete the SCP EC2 Tagging Enforcement stack and policy."
    print_warning "This action cannot be undone."
    echo ""
    
    read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleanup cancelled."
        exit 0
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "SCP EC2 Tagging Enforcement Cleanup"
    echo "=========================================="
    echo ""
    
    # Pre-cleanup checks
    check_aws_cli
    
    # Confirm deletion
    confirm_deletion
    
    # Delete stack
    delete_stack
    
    echo ""
    print_success "Cleanup completed successfully!"
    print_status "The SCP policy and CloudFormation stack have been removed."
}

# Run main function
main "$@"