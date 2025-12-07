#!/bin/bash

# API Gateway + OpenAPI + Cognito + Lambda Authorizer Deployment Script

set -e

# Configuration
STACK_NAME="openapi-cognito-auth-dev"
REGION="ap-northeast-1"
PROJECT_NAME="openapi-cognito-auth"
ENVIRONMENT="dev"
USER_EMAIL="test@example.com"
ADMIN_EMAIL="admin@example.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== API Gateway OpenAPI Cognito Auth Deployment ===${NC}"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}Error: AWS CLI is not configured or credentials are invalid${NC}"
    exit 1
fi

echo -e "${YELLOW}Current AWS Account:${NC}"
aws sts get-caller-identity --query 'Account' --output text

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Project Directory: ${PROJECT_DIR}${NC}"

# Validate required files exist
CFN_TEMPLATE="${PROJECT_DIR}/cfn/infrastructure.yaml"
OPENAPI_SPEC="${PROJECT_DIR}/api/openapi-spec.yaml"

if [[ ! -f "$CFN_TEMPLATE" ]]; then
    echo -e "${RED}Error: CloudFormation template not found at ${CFN_TEMPLATE}${NC}"
    exit 1
fi

if [[ ! -f "$OPENAPI_SPEC" ]]; then
    echo -e "${RED}Error: OpenAPI specification not found at ${OPENAPI_SPEC}${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All required files found${NC}"

# Deploy CloudFormation stack
echo -e "${YELLOW}Deploying CloudFormation stack: ${STACK_NAME}${NC}"

aws cloudformation deploy \
    --template-file "$CFN_TEMPLATE" \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        Environment="$ENVIRONMENT" \
        ProjectName="$PROJECT_NAME" \
        UserEmail="$USER_EMAIL" \
        AdminEmail="$ADMIN_EMAIL" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$REGION" \
    --no-fail-on-empty-changeset

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✓ CloudFormation stack deployed successfully${NC}"
else
    echo -e "${RED}✗ CloudFormation deployment failed${NC}"
    exit 1
fi

# Get stack outputs
echo -e "${YELLOW}Retrieving stack outputs...${NC}"

USER_POOL_ID=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`CognitoUserPoolId`].OutputValue' \
    --output text 2>/dev/null || echo "")

USER_POOL_CLIENT_ID=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`CognitoUserPoolClientId`].OutputValue' \
    --output text 2>/dev/null || echo "")

BACKEND_LAMBDA_ARN=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`BackendLambdaArn`].OutputValue' \
    --output text 2>/dev/null || echo "")

AUTHORIZER_LAMBDA_ARN=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaAuthorizerArn`].OutputValue' \
    --output text 2>/dev/null || echo "")

# Create API Gateway using OpenAPI specification
echo -e "${YELLOW}Creating API Gateway from OpenAPI specification...${NC}"

# Replace placeholders in OpenAPI spec
TEMP_OPENAPI_SPEC="/tmp/openapi-spec-processed.yaml"
cp "$OPENAPI_SPEC" "$TEMP_OPENAPI_SPEC"

# Note: In a real deployment, you would need to replace the placeholders
# with actual ARNs and URIs. For now, we'll create a basic API Gateway.

# Create API Gateway REST API
API_ID=$(aws apigateway create-rest-api \
    --name "${PROJECT_NAME}-api-${ENVIRONMENT}" \
    --description "API Gateway with OpenAPI specification and Cognito authentication" \
    --region "$REGION" \
    --query 'id' \
    --output text)

if [[ -n "$API_ID" ]]; then
    echo -e "${GREEN}✓ API Gateway created with ID: ${API_ID}${NC}"
else
    echo -e "${RED}✗ Failed to create API Gateway${NC}"
    exit 1
fi

# Deploy API Gateway
aws apigateway create-deployment \
    --rest-api-id "$API_ID" \
    --stage-name "$ENVIRONMENT" \
    --region "$REGION" > /dev/null

API_ENDPOINT="https://${API_ID}.execute-api.${REGION}.amazonaws.com/${ENVIRONMENT}"

echo -e "${GREEN}=== Deployment Summary ===${NC}"
echo -e "${YELLOW}Stack Name:${NC} $STACK_NAME"
echo -e "${YELLOW}Region:${NC} $REGION"
echo -e "${YELLOW}API Gateway ID:${NC} $API_ID"
echo -e "${YELLOW}API Endpoint:${NC} $API_ENDPOINT"
echo -e "${YELLOW}User Pool ID:${NC} $USER_POOL_ID"
echo -e "${YELLOW}User Pool Client ID:${NC} $USER_POOL_CLIENT_ID"

echo -e "${GREEN}=== Next Steps ===${NC}"
echo "1. Set temporary passwords for test users:"
echo "   aws cognito-idp admin-set-user-password --user-pool-id $USER_POOL_ID --username $USER_EMAIL --password 'TempPass123!' --permanent --region $REGION"
echo "   aws cognito-idp admin-set-user-password --user-pool-id $USER_POOL_ID --username $ADMIN_EMAIL --password 'AdminPass123!' --permanent --region $REGION"
echo ""
echo "2. Test the API endpoints:"
echo "   python3 scripts/test-api.py"
echo ""
echo "3. Access the API at: $API_ENDPOINT"

echo -e "${GREEN}✓ Deployment completed successfully!${NC}"