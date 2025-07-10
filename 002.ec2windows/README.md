# Windows EC2 Instance Setup

This Terraform configuration creates a Windows Server EC2 instance in AWS, with the following resources:

## Resource Configuration

### Network Resources
- VPC with CIDR block 10.0.0.0/16
- Public subnet (10.0.0.0/24)
- Internet Gateway
- Route Table with routes to the Internet Gateway
- Security Group for the Windows instance

### Compute Resources
- Windows Server EC2 instance:
  - Windows Server 2019 AMI (latest version from AWS)
  - Network interface with private IP 10.0.0.10
  - Public IP address
  - RDP access (port 3389)

### Access Management
- Key pair for access to the Windows instance

## Usage

Follow the instructions in the main README.md file to deploy this configuration.