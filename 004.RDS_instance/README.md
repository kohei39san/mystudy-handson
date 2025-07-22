# MySQL RDS Instance Setup

This Terraform configuration creates a MySQL RDS instance in AWS, with the following resources:

## Resource Configuration

### Network Resources
- VPC
- Two subnets in different availability zones for the DB subnet group
- Security Group for the RDS instance

### Database Resources
- MySQL RDS instance:
  - MySQL 8.0 engine
  - db.t3.micro instance class
  - 20GB GP3 storage
  - Multi-AZ deployment with DB subnet group
  - Security group with appropriate access rules

## Usage

Follow the instructions in the main README.md file to deploy this configuration.

Note: The default configuration uses "admin" as the username and "password" as the password. For production use, you should change these values and store them securely.