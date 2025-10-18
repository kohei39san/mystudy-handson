#!/bin/bash

# RDS PostgreSQL with EC2 Status Check Script
# This script checks the status of the CloudFormation stack and resources

set -e

# Configuration
STACK_NAME="rds-postgresql-ec2-stack"
REGION="ap-northeast-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== RDS PostgreSQL with EC2 Status Check ===${NC}"
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
    echo -e "${YELLOW}Stack '$STACK_NAME' not found.${NC}"
    echo "Run the deploy script to create the stack."
    exit 0
fi

echo -e "${GREEN}=== CloudFormation Stack Status ===${NC}"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Status: $STACK_STATUS"
echo ""

# Get stack outputs
echo -e "${GREEN}=== Stack Outputs ===${NC}"
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table

echo ""

# Get EC2 instance status
echo -e "${GREEN}=== EC2 Instance Status ===${NC}"
EC2_INSTANCE_ID=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`EC2InstanceId`].OutputValue' \
    --output text)

if [ -n "$EC2_INSTANCE_ID" ]; then
    EC2_STATUS=$(aws ec2 describe-instances \
        --instance-ids "$EC2_INSTANCE_ID" \
        --region "$REGION" \
        --query 'Reservations[0].Instances[0].State.Name' \
        --output text)
    
    echo "Instance ID: $EC2_INSTANCE_ID"
    echo "Status: $EC2_STATUS"
    
    # Check SSM agent status
    SSM_STATUS=$(aws ssm describe-instance-information \
        --filters "Key=InstanceIds,Values=$EC2_INSTANCE_ID" \
        --region "$REGION" \
        --query 'InstanceInformationList[0].PingStatus' \
        --output text 2>/dev/null || echo "Unknown")
    
    echo "SSM Agent Status: $SSM_STATUS"
else
    echo "EC2 Instance ID not found in stack outputs"
fi

echo ""

# Get RDS instance status
echo -e "${GREEN}=== RDS Instance Status ===${NC}"
RDS_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`RDSEndpoint`].OutputValue' \
    --output text)

if [ -n "$RDS_ENDPOINT" ]; then
    # Extract DB instance identifier from the endpoint
    DB_IDENTIFIER=$(echo "$RDS_ENDPOINT" | cut -d'.' -f1)
    
    RDS_STATUS=$(aws rds describe-db-instances \
        --db-instance-identifier "$DB_IDENTIFIER" \
        --region "$REGION" \
        --query 'DBInstances[0].DBInstanceStatus' \
        --output text 2>/dev/null || echo "Unknown")
    
    echo "DB Instance Identifier: $DB_IDENTIFIER"
    echo "Endpoint: $RDS_ENDPOINT"
    echo "Status: $RDS_STATUS"
else
    echo "RDS Endpoint not found in stack outputs"
fi

echo ""

# Connection instructions
if [ "$STACK_STATUS" = "CREATE_COMPLETE" ] || [ "$STACK_STATUS" = "UPDATE_COMPLETE" ]; then
    echo -e "${GREEN}=== Connection Instructions ===${NC}"
    
    if [ "$EC2_STATUS" = "running" ] && [ "$SSM_STATUS" = "Online" ]; then
        echo -e "${GREEN}✓ EC2 instance is ready for SSM connection${NC}"
        echo "Connect to EC2:"
        echo "  aws ssm start-session --target $EC2_INSTANCE_ID --region $REGION"
        echo ""
    else
        echo -e "${YELLOW}⚠ EC2 instance is not ready for SSM connection${NC}"
        echo "Current EC2 Status: $EC2_STATUS"
        echo "Current SSM Status: $SSM_STATUS"
        echo ""
    fi
    
    if [ "$RDS_STATUS" = "available" ]; then
        echo -e "${GREEN}✓ RDS instance is available${NC}"
        echo "After connecting to EC2, use these scripts:"
        echo "  ./connect-to-rds.sh          # Password authentication"
        echo "  ./connect-to-rds-iam.sh      # IAM authentication"
        echo ""
    else
        echo -e "${YELLOW}⚠ RDS instance is not yet available${NC}"
        echo "Current RDS Status: $RDS_STATUS"
        echo "Please wait for the RDS instance to become available."
        echo ""
    fi
else
    echo -e "${YELLOW}Stack is not in a complete state. Current status: $STACK_STATUS${NC}"
fi