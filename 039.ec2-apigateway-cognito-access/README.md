# EC2 Instance with API Gateway and Cognito Access

This project creates an EC2 instance (Amazon Linux 2023) with network access to API Gateway and includes tools for Cognito authentication and API testing.

## Architecture

The infrastructure includes:
- **EC2 Instance**: Amazon Linux 2023 with internet access
- **VPC**: Custom VPC with public subnet and internet gateway
- **Security Groups**: Configured for outbound HTTPS access to API Gateway
- **IAM Roles**: EC2 role with Cognito and CloudWatch permissions
- **Bash Script**: Comprehensive tool for Cognito authentication and API testing

## Features

### EC2 Instance
- Amazon Linux 2023 (latest AMI)
- t3.micro instance type (configurable)
- Systems Manager (SSM) access enabled
- Optional SSH access with key pair
- Pre-installed tools: AWS CLI, curl, jq, git

### Cognito API Testing Script
- Authenticate with Cognito User Pool
- Automatic token management and refresh
- Support for multiple authentication flows
- Comprehensive API testing suite
- Error handling and logging
- Configurable via environment file

### Security Features
- Minimal IAM permissions (principle of least privilege)
- Security groups restrict inbound access
- HTTPS-only communication with API Gateway
- Secure token storage with proper file permissions

## Prerequisites

- AWS CLI configured with appropriate permissions
- CloudFormation permissions to create resources
- Existing Cognito User Pool and API Gateway (for testing)

## Quick Start

### 1. Deploy Infrastructure

```bash
# Clone the repository and navigate to the project
cd 039.ec2-apigateway-cognito-access

# Make deployment script executable
chmod +x scripts/deploy.sh

# Deploy with default settings
./scripts/deploy.sh deploy

# Or deploy with custom parameters
./scripts/deploy.sh -s my-stack-name -r us-west-2 -k my-keypair deploy
```

### 2. Connect to EC2 Instance

```bash
# Using Systems Manager (recommended)
aws ssm start-session --target i-1234567890abcdef0 --region us-east-1

# Or using SSH (if key pair was specified)
ssh -i your-keypair.pem ec2-user@<public-ip>
```

### 3. Configure API Testing

```bash
# Navigate to the tools directory
cd /home/ec2-user/cognito-api-tools

# Copy and edit configuration
cp config.env.template config.env
nano config.env

# Update with your Cognito and API Gateway details
```

### 4. Test API Gateway

```bash
# Authenticate with Cognito
./cognito-api-test.sh auth

# Run full test suite
./cognito-api-test.sh test

# Refresh tokens
./cognito-api-test.sh refresh
```

## Configuration

### CloudFormation Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| EnvironmentName | ec2-apigateway-access | Environment name for resource naming |
| InstanceType | t3.micro | EC2 instance type |
| KeyPairName | (empty) | Optional EC2 Key Pair for SSH access |
| AllowedSSHCidr | 0.0.0.0/0 | CIDR block for SSH access |

### API Testing Configuration

Create `config.env` from the template and update:

```bash
# Required settings
COGNITO_USER_POOL_ID="us-east-1_XXXXXXXXX"
COGNITO_CLIENT_ID="your-client-id"
COGNITO_REGION="us-east-1"
API_GATEWAY_URL="https://api-id.execute-api.region.amazonaws.com/stage"
COGNITO_USERNAME="<email>"
COGNITO_PASSWORD="<password>"
```

## Usage Examples

### Deployment Commands

```bash
# Deploy with defaults
./scripts/deploy.sh deploy

# Deploy with custom settings
./scripts/deploy.sh -s my-stack -r us-west-2 -t t3.small deploy

# Deploy with SSH access
./scripts/deploy.sh -k my-keypair deploy

# Check stack status
./scripts/deploy.sh status

# Show stack outputs
./scripts/deploy.sh outputs

# Delete stack
./scripts/deploy.sh delete
```

### API Testing Commands

```bash
# Authenticate only
./cognito-api-test.sh auth

# Run all tests
./cognito-api-test.sh test

# Refresh access token
./cognito-api-test.sh refresh

# Clean up tokens and logs
./cognito-api-test.sh clean

# Use custom configuration
./cognito-api-test.sh -c /path/to/config.env test

# Override username and password
./cognito-api-test.sh -u user@example.com -p password auth

# Verbose output
./cognito-api-test.sh -v test
```

## Troubleshooting

### Common Issues

1. **Authentication fails**: Check Cognito User Pool configuration and user credentials
2. **API calls fail**: Verify API Gateway URL and ensure proper authentication
3. **Token refresh fails**: Check if refresh tokens are enabled in Cognito User Pool Client
4. **Network issues**: Verify security groups allow outbound HTTPS (port 443)

### Logs

- API test logs: `/home/ec2-user/cognito-api-tools/api-test.log`
- CloudWatch Logs: Check EC2 instance logs in CloudWatch
- CloudFormation events: Check stack events in AWS Console

## Security Considerations

- Store credentials securely (use AWS Secrets Manager for production)
- Limit SSH access to specific IP ranges
- Regularly rotate Cognito user passwords
- Monitor CloudWatch logs for suspicious activity
- Use IAM roles instead of hardcoded credentials

## Cleanup

```bash
# Delete CloudFormation stack
./scripts/deploy.sh delete

# Clean up local tokens and logs
./cognito-api-test.sh clean
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review CloudWatch logs
3. Verify AWS permissions and configuration
4. Check CloudFormation stack events
