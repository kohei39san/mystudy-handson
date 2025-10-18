#!/bin/bash

# RDS PostgreSQL with EC2 Cleanup Script
# This script deletes the CloudFormation stack and all associated resources

set -e

# Configuration
STACK_NAME="rds-postgresql-ec2-stack"
REGION="ap-northeast-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== RDS PostgreSQL with EC2 Cleanup ===${NC}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

# Check if stack exists
STACK_STATUS=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].StackStatus' \
    --output text 2>/dev/null || echo "STACK_NOT_FOUND")

if [ "$STACK_STATUS" = "STACK_NOT_FOUND" ]; then
    echo -e "${YELLOW}Stack '$STACK_NAME' not found. Nothing to delete.${NC}"
    exit 0
fi

echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Current Status: $STACK_STATUS"
echo ""

# Confirm deletion
echo -e "${RED}WARNING: This will delete all resources including the RDS database and Secrets Manager secret!${NC}"
echo -e "${YELLOW}Are you sure you want to delete the stack? (yes/no):${NC}"
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Cleanup cancelled.${NC}"
    exit 0
fi

echo -e "${GREEN}Deleting CloudFormation stack...${NC}"

# Delete the stack
aws cloudformation delete-stack \
    --stack-name "$STACK_NAME" \
    --region "$REGION"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Stack deletion initiated successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Monitoring stack deletion progress...${NC}"
    
    # Wait for stack deletion to complete
    aws cloudformation wait stack-delete-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Stack deleted successfully!${NC}"
    else
        echo -e "${RED}✗ Stack deletion failed or timed out${NC}"
        echo "Please check the CloudFormation console for details."
        exit 1
    fi
else
    echo -e "${RED}✗ Failed to initiate stack deletion${NC}"
    exit 1
fi