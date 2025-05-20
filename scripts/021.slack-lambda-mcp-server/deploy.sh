#!/bin/bash

set -e

# Configuration
PROJECT_DIR="021.slack-lambda-mcp-server"
SCRIPTS_DIR="scripts/021.slack-lambda-mcp-server"
SRC_DIR="src/021.slack-lambda-mcp-server"
AWS_REGION=$(grep aws_region $PROJECT_DIR/terraform.tfvars | cut -d '=' -f2 | tr -d ' "')
ECR_REPO_NAME="slack-mcp-server"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting deployment of Slack MCP Server...${NC}"

# Check if terraform.tfvars exists
if [ ! -f "$PROJECT_DIR/terraform.tfvars" ]; then
  echo -e "${YELLOW}terraform.tfvars not found. Creating from example...${NC}"
  cp $PROJECT_DIR/terraform.tfvars.example $PROJECT_DIR/terraform.tfvars
  echo -e "${RED}Please edit $PROJECT_DIR/terraform.tfvars with your values before continuing.${NC}"
  exit 1
fi

# Create SSM parameters
echo -e "${GREEN}Creating SSM parameters...${NC}"
read -p "Enter Slack Bot Token: " SLACK_BOT_TOKEN
read -p "Enter Slack Signing Secret: " SLACK_SIGNING_SECRET
read -p "Enter OpenRouter API Key: " OPENROUTER_API_KEY
read -p "Enter GitHub Repository URL: " GITHUB_REPO_URL
read -p "Enter GitHub Personal Access Token: " GITHUB_TOKEN

aws ssm put-parameter --name "/slack-mcp-bot/SLACK_BOT_TOKEN" --value "$SLACK_BOT_TOKEN" --type "SecureString" --overwrite --region $AWS_REGION
aws ssm put-parameter --name "/slack-mcp-bot/SLACK_SIGNING_SECRET" --value "$SLACK_SIGNING_SECRET" --type "SecureString" --overwrite --region $AWS_REGION
aws ssm put-parameter --name "/slack-mcp-bot/OPENROUTER_API_KEY" --value "$OPENROUTER_API_KEY" --type "SecureString" --overwrite --region $AWS_REGION
aws ssm put-parameter --name "/slack-mcp-bot/GITHUB_REPO_URL" --value "$GITHUB_REPO_URL" --type "SecureString" --overwrite --region $AWS_REGION
aws ssm put-parameter --name "/slack-mcp-bot/GITHUB_TOKEN" --value "$GITHUB_TOKEN" --type "SecureString" --overwrite --region $AWS_REGION

# Initialize Terraform
echo -e "${GREEN}Initializing Terraform...${NC}"
cd $PROJECT_DIR
terraform init

# Apply Terraform to create initial resources
echo -e "${GREEN}Creating initial resources...${NC}"
terraform apply -target=aws_ecr_repository.mcp_server -auto-approve

# Get ECR repository URL
ECR_REPO_URL=$(terraform output -raw ecr_repository_url)
echo -e "${GREEN}ECR Repository URL: $ECR_REPO_URL${NC}"

# Build and push Docker image
echo -e "${GREEN}Building and pushing Docker image...${NC}"
cd ..
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URL

# Copy files to a temporary directory for Docker build
TEMP_DIR=$(mktemp -d)
cp $SRC_DIR/docker/Dockerfile $TEMP_DIR/
cp $SRC_DIR/docker/requirements.txt $TEMP_DIR/
cp $SCRIPTS_DIR/py/lambda_function.py $TEMP_DIR/

# Create mcp_servers directory
mkdir -p $TEMP_DIR/mcp_servers

# Build and push the Docker image
docker build -t $ECR_REPO_URL:latest $TEMP_DIR
docker push $ECR_REPO_URL:latest

# Clean up
rm -rf $TEMP_DIR

# Deploy CloudFormation for Bedrock Knowledge Base
echo -e "${GREEN}Deploying CloudFormation for Bedrock Knowledge Base...${NC}"
S3_BUCKET_NAME=$(grep s3_bucket_name $PROJECT_DIR/terraform.tfvars | cut -d '=' -f2 | tr -d ' "')
OPENSEARCH_DOMAIN_NAME=$(grep opensearch_domain_name $PROJECT_DIR/terraform.tfvars | cut -d '=' -f2 | tr -d ' "')

aws cloudformation deploy \
  --template-file $SRC_DIR/bedrock-kb-cfn.yaml \
  --stack-name slack-mcp-bedrock-kb \
  --parameter-overrides \
    S3BucketName=$S3_BUCKET_NAME \
    OpenSearchDomainName=$OPENSEARCH_DOMAIN_NAME \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION

# Get Bedrock Knowledge Base ID
BEDROCK_KB_ID=$(aws cloudformation describe-stacks --stack-name slack-mcp-bedrock-kb --query "Stacks[0].Outputs[?OutputKey=='KnowledgeBaseId'].OutputValue" --output text --region $AWS_REGION)
echo -e "${GREEN}Bedrock Knowledge Base ID: $BEDROCK_KB_ID${NC}"

# Update terraform.tfvars with Bedrock Knowledge Base ID
sed -i "s/bedrock_kb_id *= *\".*\"/bedrock_kb_id = \"$BEDROCK_KB_ID\"/" $PROJECT_DIR/terraform.tfvars

# Apply Terraform for remaining resources
echo -e "${GREEN}Deploying remaining resources...${NC}"
cd $PROJECT_DIR
terraform apply -auto-approve

# Get outputs
API_GATEWAY_URL=$(terraform output -raw api_gateway_url)

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${YELLOW}API Gateway URL: $API_GATEWAY_URL${NC}"
echo -e "${YELLOW}Update your Slack app with this URL.${NC}"