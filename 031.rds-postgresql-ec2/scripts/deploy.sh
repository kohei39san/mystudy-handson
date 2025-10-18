#!/bin/bash

# RDS PostgreSQL with EC2 Deployment Script
# This script deploys the CloudFormation stack for RDS PostgreSQL with EC2 access

set -e

# Configuration
STACK_NAME="rds-postgresql-ec2-stack"
TEMPLATE_FILE="../cfn/rds-postgresql-ec2.yaml"
REGION="ap-northeast-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== RDS PostgreSQL with EC2 Deployment ===${NC}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

# Check if template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: Template file not found: $TEMPLATE_FILE${NC}"
    exit 1
fi

# Prompt for database password
echo -e "${YELLOW}Please enter a password for the PostgreSQL database (8-128 characters):${NC}"
read -s DB_PASSWORD
echo ""

if [ ${#DB_PASSWORD} -lt 8 ]; then
    echo -e "${RED}Error: Password must be at least 8 characters long${NC}"
    exit 1
fi

echo -e "${GREEN}Deploying CloudFormation stack...${NC}"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Template: $TEMPLATE_FILE"
echo ""

# Deploy the stack
aws cloudformation deploy \
    --template-file "$TEMPLATE_FILE" \
    --stack-name "$STACK_NAME" \
    --parameter-overrides DBPassword="$DB_PASSWORD" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$REGION"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Stack deployed successfully!${NC}"
    echo ""
    
    # Get stack outputs
    echo -e "${GREEN}=== Stack Outputs ===${NC}"
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
    
    echo ""
    echo -e "${GREEN}=== Next Steps ===${NC}"
    echo "1. Wait for the RDS instance to be available (this may take 5-10 minutes)"
    echo "2. Use the SSM connect command from the outputs to connect to the EC2 instance"
    echo "3. Run the connection scripts on the EC2 instance to connect to PostgreSQL"
    echo ""
    
    # Get EC2 instance ID for SSM connection
    EC2_INSTANCE_ID=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`EC2InstanceId`].OutputValue' \
        --output text)
    
    echo -e "${YELLOW}To connect to EC2 via Systems Manager:${NC}"
    echo "aws ssm start-session --target $EC2_INSTANCE_ID --region $REGION"
    echo ""
    
else
    echo -e "${RED}✗ Stack deployment failed${NC}"
    exit 1
fi