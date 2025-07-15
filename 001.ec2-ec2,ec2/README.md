# EC2 Bastion and Private Server Setup

This Terraform configuration creates a bastion host and a private server in AWS, with the following resources:

## Resource Configuration

### Network Resources
- VPC with CIDR block 10.0.0.0/16
- Public subnet for the bastion host (10.0.0.0/24)
- Private subnet for the private server (10.0.1.0/24)
- Internet Gateway
- Route Table with routes to the Internet Gateway
- Security Groups for both instances

### Compute Resources
- Bastion Host EC2 instance:
  - Amazon Linux 2 AMI (from SSM Parameter Store)
  - Network interface with private IP 10.0.0.10
  - Public IP address
  - SSH access

- Private Server EC2 instance:
  - Amazon Linux 2 AMI (from SSM Parameter Store)
  - Network interface with private IP 10.0.1.10
  - SSH access only from the bastion host
  - Bootstrap script for initial configuration

### Access Management
- Key pair for SSH access to both instances

## Usage

Follow the instructions in the main README.md file to deploy this configuration.