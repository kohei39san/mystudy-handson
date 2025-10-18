#!/bin/bash

# CloudFormation Template Validation Script
# This script validates the CloudFormation template syntax

set -e

# Configuration
TEMPLATE_FILE="../cfn/rds-postgresql-ec2.yaml"
REGION="ap-northeast-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== CloudFormation Template Validation ===${NC}"
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

echo "Template File: $TEMPLATE_FILE"
echo "Region: $REGION"
echo ""

# Validate the template
echo -e "${YELLOW}Validating CloudFormation template...${NC}"

aws cloudformation validate-template \
    --template-body file://$TEMPLATE_FILE \
    --region $REGION

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Template validation successful!${NC}"
    echo ""
    
    # Show template summary
    echo -e "${GREEN}=== Template Summary ===${NC}"
    aws cloudformation validate-template \
        --template-body file://$TEMPLATE_FILE \
        --region $REGION \
        --query '{Parameters:Parameters[*].{ParameterKey:ParameterKey,DefaultValue:DefaultValue,Description:Description},Capabilities:Capabilities}' \
        --output table
    
else
    echo -e "${RED}✗ Template validation failed${NC}"
    exit 1
fi