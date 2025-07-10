# Linux Managed Node Setup

This Terraform configuration creates a Linux EC2 instance managed by AWS Systems Manager with monitoring capabilities, with the following resources:

## Resource Configuration

### Network Resources
- VPC
- Public subnet
- Internet Gateway
- Route Table with routes to the Internet Gateway
- Security Group for the Linux instance

### Compute Resources
- Linux EC2 instance:
  - Amazon Linux AMI (specified via variable)
  - IAM instance profile for Systems Manager management
  - Key pair for SSH access if needed

### IAM Resources
- IAM role with EC2 trust relationship
- IAM policy attachment for AmazonSSMManagedInstanceCore
- IAM instance profile for the EC2 instance

### Monitoring Resources
- Installation scripts for:
  - Amazon CloudWatch Agent
  - Zabbix Agent 6.0

## Usage

Follow the instructions in the main README.md file to deploy this configuration.

After deployment, you can:
1. Manage this Linux instance through AWS Systems Manager
2. Monitor the instance using Amazon CloudWatch
3. Monitor the instance using Zabbix (requires a Zabbix server configuration)
4. Access the instance via SSH using the key pair if required