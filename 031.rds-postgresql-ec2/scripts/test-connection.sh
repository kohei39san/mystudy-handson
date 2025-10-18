#!/bin/bash

# RDS PostgreSQL Connection Test Script
# This script tests the connection to RDS PostgreSQL from EC2
# Run this script on the EC2 instance after deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== RDS PostgreSQL Connection Test ===${NC}"
echo ""

# Load environment variables
if [ -f "rds-env.sh" ]; then
    source rds-env.sh
    echo -e "${GREEN}Environment variables loaded${NC}"
else
    echo -e "${RED}Error: rds-env.sh not found${NC}"
    echo "Please ensure you are running this on the EC2 instance created by the CloudFormation stack"
    exit 1
fi

echo "RDS Endpoint: $RDS_ENDPOINT"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Region: $AWS_REGION"
echo ""

# Test 1: Check if PostgreSQL client is installed
echo -e "${YELLOW}Test 1: Checking PostgreSQL client installation...${NC}"
if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version)
    echo -e "${GREEN}✓ PostgreSQL client is installed: $PSQL_VERSION${NC}"
else
    echo -e "${RED}✗ PostgreSQL client is not installed${NC}"
    exit 1
fi
echo ""

# Test 2: Check if AWS CLI is installed and configured
echo -e "${YELLOW}Test 2: Checking AWS CLI installation and configuration...${NC}"
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    echo -e "${GREEN}✓ AWS CLI is installed: $AWS_VERSION${NC}"
    
    # Check if we can get AWS identity
    if aws sts get-caller-identity &> /dev/null; then
        IDENTITY=$(aws sts get-caller-identity --query 'Arn' --output text)
        echo -e "${GREEN}✓ AWS CLI is configured: $IDENTITY${NC}"
    else
        echo -e "${RED}✗ AWS CLI is not properly configured${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ AWS CLI is not installed${NC}"
    exit 1
fi
echo ""

# Test 3: Check network connectivity to RDS
echo -e "${YELLOW}Test 3: Checking network connectivity to RDS...${NC}"
if nc -z $RDS_ENDPOINT 5432 2>/dev/null; then
    echo -e "${GREEN}✓ Network connectivity to RDS is working${NC}"
else
    echo -e "${RED}✗ Cannot connect to RDS endpoint${NC}"
    echo "Please check:"
    echo "  - RDS instance is in 'available' state"
    echo "  - Security groups allow connection from EC2 to RDS"
    echo "  - Network ACLs are not blocking the connection"
    exit 1
fi
echo ""

# Test 4: Test IAM authentication token generation
echo -e "${YELLOW}Test 4: Testing IAM authentication token generation...${NC}"
TOKEN=$(aws rds generate-db-auth-token --hostname $RDS_ENDPOINT --port 5432 --username $DB_USER --region $AWS_REGION 2>/dev/null)
if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓ IAM authentication token generated successfully${NC}"
    echo "Token length: ${#TOKEN} characters"
else
    echo -e "${RED}✗ Failed to generate IAM authentication token${NC}"
    echo "Please check:"
    echo "  - EC2 instance has proper IAM role attached"
    echo "  - IAM role has rds-db:connect permission"
    echo "  - RDS instance has IAM database authentication enabled"
    exit 1
fi
echo ""

# Test 5: Test basic PostgreSQL connection (this will prompt for password)
echo -e "${YELLOW}Test 5: Testing PostgreSQL connection with password authentication...${NC}"
echo "This test will prompt for the database password."
echo "Enter the password you set during CloudFormation deployment:"

if psql -h $RDS_ENDPOINT -p 5432 -U $DB_USER -d $DB_NAME -c "SELECT version();" 2>/dev/null; then
    echo -e "${GREEN}✓ Password authentication successful${NC}"
else
    echo -e "${RED}✗ Password authentication failed${NC}"
    echo "Please check:"
    echo "  - Correct password is being used"
    echo "  - RDS instance is accepting connections"
    echo "  - Database user exists and has proper permissions"
fi
echo ""

# Test 6: Test IAM authentication (non-interactive)
echo -e "${YELLOW}Test 6: Testing PostgreSQL connection with IAM authentication...${NC}"
if PGPASSWORD=$TOKEN psql -h $RDS_ENDPOINT -p 5432 -U $DB_USER -d $DB_NAME -c "SELECT current_user, session_user;" 2>/dev/null; then
    echo -e "${GREEN}✓ IAM authentication successful${NC}"
else
    echo -e "${RED}✗ IAM authentication failed${NC}"
    echo "This is expected if IAM database user hasn't been created yet."
    echo "To enable IAM authentication, connect with password and run:"
    echo "  CREATE USER $DB_USER WITH LOGIN;"
    echo "  GRANT rds_iam TO $DB_USER;"
fi
echo ""

echo -e "${BLUE}=== Connection Test Complete ===${NC}"
echo ""
echo -e "${GREEN}Available connection scripts:${NC}"
echo "  ./connect-to-rds.sh      - Password authentication"
echo "  ./connect-to-rds-iam.sh  - IAM authentication (after setup)"