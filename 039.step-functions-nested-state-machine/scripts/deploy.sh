#!/bin/bash

# Deployment script for nested Step Functions state machine
# This script deploys the infrastructure using either Terraform or CloudFormation

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "===== Nested Step Functions State Machine Deployment ====="
echo "Project Directory: $PROJECT_DIR"
echo ""

# Function to deploy with Terraform
deploy_terraform() {
    echo "Deploying with Terraform..."
    
    # Initialize Terraform
    echo "Initializing Terraform..."
    terraform init
    
    # Validate configuration
    echo "Validating Terraform configuration..."
    terraform validate
    
    # Plan deployment
    echo "Planning deployment..."
    terraform plan
    
    # Apply deployment
    read -p "Do you want to apply the deployment? (yes/no): " confirm
    if [ "$confirm" == "yes" ]; then
        terraform apply -auto-approve
        echo ""
        echo "===== Deployment Complete ====="
        echo "Getting outputs..."
        terraform output
    else
        echo "Deployment cancelled."
        exit 0
    fi
}

# Function to deploy with CloudFormation
deploy_cloudformation() {
    echo "Deploying with CloudFormation..."
    
    STACK_NAME="${1:-nested-sfn-study-dev}"
    TEMPLATE_FILE="cfn/infrastructure.yaml"
    REGION="ap-northeast-1"
    
    echo "Stack Name: $STACK_NAME"
    echo "Template: $TEMPLATE_FILE"
    echo "Region: $REGION"
    echo ""
    
    # Validate template
    echo "Validating CloudFormation template..."
    aws cloudformation validate-template \
        --template-body file://$TEMPLATE_FILE \
        --region $REGION
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &>/dev/null; then
        echo "Stack exists. Updating..."
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://$TEMPLATE_FILE \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $REGION
        
        echo "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete \
            --stack-name $STACK_NAME \
            --region $REGION
    else
        echo "Creating new stack..."
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://$TEMPLATE_FILE \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $REGION
        
        echo "Waiting for stack creation to complete..."
        aws cloudformation wait stack-create-complete \
            --stack-name $STACK_NAME \
            --region $REGION
    fi
    
    echo ""
    echo "===== Deployment Complete ====="
    echo "Getting stack outputs..."
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs' \
        --output table
}

# Main menu
echo "Select deployment method:"
echo "1) Terraform"
echo "2) CloudFormation"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        deploy_terraform
        ;;
    2)
        read -p "Enter stack name (default: nested-sfn-study-dev): " stack_name
        deploy_cloudformation "${stack_name:-nested-sfn-study-dev}"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "===== Next Steps ====="
echo "1. Test the deployment using: python scripts/test_execution.py"
echo "2. Check CloudWatch Logs for Lambda and Step Functions execution logs"
echo "3. View execution history in AWS Step Functions console"
