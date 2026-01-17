#!/bin/bash

# EC2 API Gateway Cognito Access - CloudFormation Deployment Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE_FILE="$PROJECT_DIR/cfn/ec2-apigateway-access.yaml"

STACK_NAME="ec2-apigateway-cognito-access"
REGION="us-east-1"
INSTANCE_TYPE="t3.micro"
ENVIRONMENT="ec2-apigateway-access"

usage() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  deploy    Deploy CloudFormation stack"
    echo "  delete    Delete CloudFormation stack"
    echo "  status    Show stack status"
    echo "  outputs   Show stack outputs"
    echo ""
    echo "Options:"
    echo "  -s NAME   Stack name (default: $STACK_NAME)"
    echo "  -r REGION AWS region (default: $REGION)"
    echo "  -t TYPE   Instance type (default: $INSTANCE_TYPE)"
    echo "  -k NAME   Key pair name (optional)"
    echo "  -e NAME   Environment name (default: $ENVIRONMENT)"
    echo "  -h        Show this help"
}

check_aws() {
    if ! command -v aws >/dev/null 2>&1; then
        echo "Error: AWS CLI not found"
        exit 1
    fi
    
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo "Error: AWS credentials not configured"
        exit 1
    fi
}

validate_template() {
    echo "Validating CloudFormation template..."
    aws cloudformation validate-template \
        --template-body "file://$TEMPLATE_FILE" \
        --region "$REGION" >/dev/null
    echo "Template validation successful"
}

deploy() {
    echo "Deploying stack: $STACK_NAME"
    
    PARAMS="ParameterKey=EnvironmentName,ParameterValue=$ENVIRONMENT"
    PARAMS="$PARAMS ParameterKey=InstanceType,ParameterValue=$INSTANCE_TYPE"
    
    if [ -n "${KEY_PAIR:-}" ]; then
        PARAMS="$PARAMS ParameterKey=KeyPairName,ParameterValue=$KEY_PAIR"
    fi
    
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" >/dev/null 2>&1; then
        echo "Updating existing stack..."
        aws cloudformation update-stack \
            --stack-name "$STACK_NAME" \
            --template-body "file://$TEMPLATE_FILE" \
            --parameters $PARAMS \
            --capabilities CAPABILITY_NAMED_IAM \
            --region "$REGION"
        
        aws cloudformation wait stack-update-complete \
            --stack-name "$STACK_NAME" \
            --region "$REGION"
    else
        echo "Creating new stack..."
        aws cloudformation create-stack \
            --stack-name "$STACK_NAME" \
            --template-body "file://$TEMPLATE_FILE" \
            --parameters $PARAMS \
            --capabilities CAPABILITY_NAMED_IAM \
            --region "$REGION"
        
        aws cloudformation wait stack-create-complete \
            --stack-name "$STACK_NAME" \
            --region "$REGION"
    fi
    
    echo "Deployment completed successfully!"
    show_outputs
}

delete_stack() {
    echo "Deleting stack: $STACK_NAME"
    aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$REGION"
    aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region "$REGION"
    echo "Stack deleted successfully"
}

show_status() {
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].{Name:StackName,Status:StackStatus}' \
        --output table
}

show_outputs() {
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[*].{Key:OutputKey,Value:OutputValue}' \
        --output table
}

while getopts "s:r:t:k:e:h" opt; do
    case $opt in
        s) STACK_NAME="$OPTARG" ;;
        r) REGION="$OPTARG" ;;
        t) INSTANCE_TYPE="$OPTARG" ;;
        k) KEY_PAIR="$OPTARG" ;;
        e) ENVIRONMENT="$OPTARG" ;;
        h) usage; exit 0 ;;
        *) usage; exit 1 ;;
    esac
done

shift $((OPTIND-1))
COMMAND="${1:-help}"

check_aws

case "$COMMAND" in
    deploy)
        validate_template
        deploy
        ;;
    delete)
        delete_stack
        ;;
    status)
        show_status
        ;;
    outputs)
        show_outputs
        ;;
    *)
        usage
        exit 1
        ;;
esac
