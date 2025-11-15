#!/bin/bash

# SCP EC2 Tagging Enforcement - Deploy Script
# This script deploys the CloudFormation template for SCP EC2 tagging enforcement

set -e

# Configuration
STACK_NAME="scp-ec2-tagging-enforcement"
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

# Function to check if running in Organizations management account
check_organizations_account() {
    print_status "Checking if this is an Organizations management account..."
    
    if ! aws organizations describe-organization &> /dev/null; then
        print_error "This account is not an Organizations management account or doesn't have Organizations enabled."
        print_error "SCP policies can only be created from the Organizations management account."
        exit 1
    fi
    
    print_success "Organizations management account confirmed."
}

# Function to validate CloudFormation template
validate_template() {
    print_status "Validating CloudFormation template..."
    
    if aws cloudformation validate-template --template-body file://$TEMPLATE_FILE --region $REGION > /dev/null; then
        print_success "Template validation successful."
    else
        print_error "Template validation failed."
        exit 1
    fi
}

# Function to check if stack exists
stack_exists() {
    aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &> /dev/null
}

# Function to deploy or update stack
deploy_stack() {
    if stack_exists; then
        print_status "Stack $STACK_NAME exists. Updating..."
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://$TEMPLATE_FILE \
            --region $REGION \
            --capabilities CAPABILITY_IAM
        
        print_status "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete \
            --stack-name $STACK_NAME \
            --region $REGION
        
        print_success "Stack update completed successfully."
    else
        print_status "Creating new stack $STACK_NAME..."
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://$TEMPLATE_FILE \
            --region $REGION \
            --capabilities CAPABILITY_IAM
        
        print_status "Waiting for stack creation to complete..."
        aws cloudformation wait stack-create-complete \
            --stack-name $STACK_NAME \
            --region $REGION
        
        print_success "Stack creation completed successfully."
    fi
}

# Function to get stack outputs
get_stack_outputs() {
    print_status "Retrieving stack outputs..."
    
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
}

# Function to display next steps
display_next_steps() {
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    print_warning "IMPORTANT NEXT STEPS:"
    echo "1. The SCP policy has been created but not yet attached to any organizational units (OUs)."
    echo "2. To attach the policy to an OU, use the AWS Organizations console or CLI:"
    echo "   aws organizations attach-policy --policy-id <POLICY_ID> --target-id <OU_ID>"
    echo "3. Test the policy in a non-production environment first."
    echo "4. Monitor CloudTrail logs for any denied actions after applying the policy."
    echo ""
    print_warning "Remember: This policy will deny EC2 instance creation without required tags!"
}

# Main execution
main() {
    echo "=========================================="
    echo "SCP EC2 Tagging Enforcement Deployment"
    echo "=========================================="
    echo ""
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Pre-deployment checks
    check_aws_cli
    check_organizations_account
    validate_template
    
    # Deploy stack
    deploy_stack
    
    # Show results
    get_stack_outputs
    display_next_steps
}

# Run main function
main "$@"