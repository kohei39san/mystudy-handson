#!/bin/bash

# Aurora Mock Testing Project Deployment Script
# This script deploys the CloudFormation stacks and Terraform resources

set -e

PROJECT_NAME="aurora-mock-testing"
ENVIRONMENT="dev"
AWS_REGION="ap-northeast-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is configured
check_aws_cli() {
    echo_info "Checking AWS CLI configuration..."
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        echo_error "AWS CLI is not configured or credentials are invalid"
        exit 1
    fi
    echo_info "AWS CLI is configured"
}

# Deploy Terraform resources
deploy_terraform() {
    echo_info "Deploying Terraform resources..."
    
    terraform init
    terraform plan -var="project_name=${PROJECT_NAME}" -var="environment=${ENVIRONMENT}"
    terraform apply -var="project_name=${PROJECT_NAME}" -var="environment=${ENVIRONMENT}" -auto-approve
    
    echo_info "Terraform deployment completed"
}

# Get VPC and subnet information (assuming default VPC for demo)
get_vpc_info() {
    echo_info "Getting VPC and subnet information..."
    
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region ${AWS_REGION})
    SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${VPC_ID}" --query 'Subnets[].SubnetId' --output text --region ${AWS_REGION} | tr '\t' ',')
    
    if [ "$VPC_ID" == "None" ] || [ -z "$SUBNET_IDS" ]; then
        echo_error "Could not find default VPC or subnets"
        exit 1
    fi
    
    echo_info "Using VPC: $VPC_ID"
    echo_info "Using Subnets: $SUBNET_IDS"
}

# Deploy CloudFormation stacks
deploy_cloudformation() {
    echo_info "Deploying CloudFormation stacks..."
    
    # Deploy Aurora stack
    echo_info "Deploying Aurora stack..."
    aws cloudformation deploy \
        --template-file cfn/aurora.yaml \
        --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-aurora" \
        --parameter-overrides \
            ProjectName=${PROJECT_NAME} \
            Environment=${ENVIRONMENT} \
            VpcId=${VPC_ID} \
            SubnetIds=${SUBNET_IDS} \
        --capabilities CAPABILITY_NAMED_IAM \
        --region ${AWS_REGION}
    
    # Get Aurora endpoint
    AURORA_ENDPOINT=$(aws cloudformation describe-stacks \
        --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-aurora" \
        --query 'Stacks[0].Outputs[?OutputKey==`AuroraClusterEndpoint`].OutputValue' \
        --output text \
        --region ${AWS_REGION})
    
    # Deploy Secrets Manager stack
    echo_info "Deploying Secrets Manager stack..."
    aws cloudformation deploy \
        --template-file cfn/secrets-manager.yaml \
        --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-secrets" \
        --parameter-overrides \
            ProjectName=${PROJECT_NAME} \
            Environment=${ENVIRONMENT} \
            AuroraEndpoint=${AURORA_ENDPOINT} \
        --capabilities CAPABILITY_NAMED_IAM \
        --region ${AWS_REGION}
    
    # Get Secrets Manager ARN
    SECRET_ARN=$(aws cloudformation describe-stacks \
        --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-secrets" \
        --query 'Stacks[0].Outputs[?OutputKey==`AuroraSecretArn`].OutputValue' \
        --output text \
        --region ${AWS_REGION})
    
    # Get ECS Security Group ID
    ECS_SG_ID=$(aws cloudformation describe-stacks \
        --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-aurora" \
        --query 'Stacks[0].Outputs[?OutputKey==`ECSSecurityGroupId`].OutputValue' \
        --output text \
        --region ${AWS_REGION})
    
    # Deploy ECS stack
    echo_info "Deploying ECS stack..."
    aws cloudformation deploy \
        --template-file cfn/ecs.yaml \
        --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-ecs" \
        --parameter-overrides \
            ProjectName=${PROJECT_NAME} \
            Environment=${ENVIRONMENT} \
            VpcId=${VPC_ID} \
            SubnetIds=${SUBNET_IDS} \
            ECSSecurityGroupId=${ECS_SG_ID} \
        --capabilities CAPABILITY_NAMED_IAM \
        --region ${AWS_REGION}
    
    # Get API URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-ecs" \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
        --output text \
        --region ${AWS_REGION})
    
    # Get Lambda Security Group ID
    LAMBDA_SG_ID=$(aws cloudformation describe-stacks \
        --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-aurora" \
        --query 'Stacks[0].Outputs[?OutputKey==`LambdaSecurityGroupId`].OutputValue' \
        --output text \
        --region ${AWS_REGION})
    
    # Deploy Lambda stack
    echo_info "Deploying Lambda stack..."
    aws cloudformation deploy \
        --template-file cfn/lambda.yaml \
        --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-lambda" \
        --parameter-overrides \
            ProjectName=${PROJECT_NAME} \
            Environment=${ENVIRONMENT} \
            VpcId=${VPC_ID} \
            SubnetIds=${SUBNET_IDS} \
            LambdaSecurityGroupId=${LAMBDA_SG_ID} \
            AuroraSecretArn=${SECRET_ARN} \
            ApiUrl=${API_URL} \
        --capabilities CAPABILITY_NAMED_IAM \
        --region ${AWS_REGION}
    
    echo_info "CloudFormation deployment completed"
}

# Main deployment function
main() {
    echo_info "Starting deployment of Aurora Mock Testing Project..."
    
    check_aws_cli
    get_vpc_info
    deploy_terraform
    deploy_cloudformation
    
    echo_info "Deployment completed successfully!"
    echo_info "API URL: ${API_URL}"
    echo_info "Aurora Endpoint: ${AURORA_ENDPOINT}"
}

# Run main function
main "$@"