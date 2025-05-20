# Slack Chatbot with OpenRouter and AWS MCP Server Integration

This project implements a Slack chatbot that integrates with OpenRouter and AWS MCP Servers (AWS Documentation and Amazon Bedrock Knowledge Bases Retrieval) to provide intelligent responses to user queries.

## Architecture Overview

The solution consists of the following components:

1. **Slack App**: Receives messages from channel members and forwards them to AWS Lambda.
2. **Message Receiver Lambda**: JavaScript-based Lambda function using Bolt.js that receives messages from Slack.
3. **MCP Server Lambda**: Python-based Lambda function that runs AWS Documentation and Bedrock Knowledge Bases Retrieval MCP Servers locally and queries OpenRouter.
4. **DynamoDB**: Stores conversation history and caches interactions between Slack and Lambda.
5. **Amazon Bedrock Knowledge Base**: Provides knowledge retrieval capabilities using data stored in S3.
6. **S3 Bucket**: Stores data for the Bedrock knowledge base.
7. **EventBridge + Lambda**: Periodically syncs content from a private GitHub repository to the S3 bucket.
8. **Amazon OpenSearch**: Serves as the vector database for the Bedrock knowledge base.

## Prerequisites

Before deploying this solution, you'll need:

1. **AWS Account** with permissions to create the required resources
2. **Slack Workspace** where you can create a new app
3. **OpenRouter API Key** for accessing LLM capabilities
4. **GitHub Repository** containing the knowledge base documents
5. **GitHub Personal Access Token** with repo access

## Deployment Instructions

### 1. Prepare the Environment

Clone this repository and navigate to the project directory:

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Configure Terraform Variables

Copy the example variables file and edit it with your values:

```bash
cp 021.slack-lambda-mcp-server/terraform.tfvars.example 021.slack-lambda-mcp-server/terraform.tfvars
```

Edit the `terraform.tfvars` file with your preferred settings. Make sure to set a unique S3 bucket name.

### 3. Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps) and click "Create New App"
2. Choose "From an app manifest" and select your workspace
3. Copy the contents of `src/021.slack-lambda-mcp-server/slack-app.json` and paste it into the manifest editor
4. Replace `${API_GATEWAY_URL}` with a placeholder (we'll update it later)
5. Click "Create" and note down the "Bot User OAuth Token" and "Signing Secret" from the "Basic Information" page

### 4. Run the Deployment Script

The deployment script will:
- Create SSM parameters for secrets
- Initialize Terraform
- Build and push the Docker image for the MCP Server Lambda
- Deploy the CloudFormation stack for Bedrock Knowledge Base
- Deploy the remaining Terraform resources

```bash
chmod +x scripts/021.slack-lambda-mcp-server/deploy.sh
./scripts/021.slack-lambda-mcp-server/deploy.sh
```

When prompted, enter:
- Slack Bot Token (starts with `xoxb-`)
- Slack Signing Secret
- OpenRouter API Key
- GitHub Repository URL (e.g., `https://github.com/username/repo`)
- GitHub Personal Access Token

### 5. Update the Slack App Configuration

After deployment completes, you'll receive an API Gateway URL. Update your Slack app:

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps) and select your app
2. Navigate to "Event Subscriptions"
3. Enable events and enter the API Gateway URL
4. Navigate to "Interactivity & Shortcuts"
5. Enable interactivity and enter the same API Gateway URL
6. Click "Save Changes"

### 6. Install the App to Your Workspace

1. Go to "OAuth & Permissions" in your Slack app settings
2. Click "Install to Workspace"
3. Authorize the app

## Usage

Once deployed, you can interact with the bot in two ways:

1. **Direct Messages**: Send a message directly to the bot
2. **Mentions**: Mention the bot in a channel with `@BotName`

Example queries:
- "How do I set up an S3 bucket?"
- "What are the best practices for securing an EC2 instance?"
- "Can you explain how AWS Lambda works?"

## Component Details

### Slack App
- Uses OAuth with minimal permissions required for operation
- Configured to listen to channel messages and interact with users
- Sends messages to the Message Receiver Lambda via API Gateway

### Message Receiver Lambda
- Implemented using JavaScript and the Bolt.js framework
- Authenticates and processes incoming Slack events
- Forwards user queries to the MCP Server Lambda
- Returns responses back to Slack
- Stores authentication credentials in AWS Systems Manager Parameter Store

### MCP Server Lambda
- Containerized Lambda function that runs MCP Servers locally
- Integrates with OpenRouter to process queries with consideration for MCP Server tools
- Runs both AWS Documentation and Amazon Bedrock Knowledge Bases Retrieval MCP Servers
- Stores conversation history in DynamoDB
- Returns formatted responses to the Message Receiver Lambda

### DynamoDB
- Optimized for minimal cost while maintaining performance
- Stores conversation history with TTL for automatic cleanup
- Uses on-demand capacity for cost efficiency

### Amazon Bedrock Knowledge Base
- Configured to use S3 as the data source
- Integrates with OpenSearch for vector embeddings
- Provides retrieval capabilities for the MCP Server

### S3 Data Source
- Stores documents and data for the knowledge base
- Updated periodically from a private GitHub repository

### EventBridge + Lambda
- Scheduled to sync content from GitHub to S3 at regular intervals
- Ensures the knowledge base has the latest information

### Amazon OpenSearch
- Configured for minimal cost (t3.small.search instance type)
- Serves as the vector database for the Bedrock knowledge base
- Uses standard (non-serverless) deployment for cost efficiency

## Customization

### Adding Custom Knowledge

To add custom knowledge to the bot:
1. Add documents to your GitHub repository
2. The GitHub to S3 sync Lambda will automatically sync them to S3
3. The Bedrock Knowledge Base will index the new documents

Supported file formats:
- Markdown (.md)
- PDF (.pdf)
- Text (.txt)
- HTML (.html)
- Microsoft Office documents (.docx, .xlsx, .pptx)

### Modifying the MCP Server Configuration

To modify the MCP Server configuration:
1. Edit the Docker container code in `src/021.slack-lambda-mcp-server/docker/`
2. Rebuild and push the Docker image
3. Update the Lambda function

## Troubleshooting

### Common Issues

1. **Slack App Not Responding**:
   - Check CloudWatch Logs for the Slack Receiver Lambda
   - Verify the API Gateway URL is correctly configured in Slack

2. **MCP Server Errors**:
   - Check CloudWatch Logs for the MCP Server Lambda
   - Verify the OpenRouter API key is valid

3. **Knowledge Base Not Working**:
   - Check the CloudFormation stack status
   - Verify the S3 bucket contains documents
   - Check OpenSearch domain status

## Security Considerations

- All sensitive information is stored in AWS Systems Manager Parameter Store
- IAM roles follow the principle of least privilege
- API endpoints are secured with appropriate authentication
- Network traffic is encrypted in transit

## Monitoring and Maintenance

- CloudWatch Logs are configured for all Lambda functions
- CloudWatch Alarms can be set up to monitor for errors
- Regular updates to dependencies are recommended to maintain security

## Cost Optimization

This solution is designed to minimize costs:
- DynamoDB uses on-demand capacity
- OpenSearch uses t3.small.search instances
- Lambda functions use minimal memory and timeout settings
- S3 lifecycle policies can be added to manage storage costs