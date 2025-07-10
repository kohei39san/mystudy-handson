# Aurora MySQL RDS Cluster Setup

This Terraform configuration creates an Aurora MySQL RDS cluster in AWS, with the following resources:

## Resource Configuration

### Network Resources
- VPC
- Two subnets in different availability zones for the DB subnet group
- Security Group for the RDS cluster

### Database Resources
- Aurora MySQL RDS cluster:
  - Aurora MySQL 8.0 engine (version 8.0.mysql_aurora.3.05.2)
  - Database name: "mydb"
  - Backup retention period: 1 day
  - Preferred backup window: 07:00-09:00 UTC

- RDS Cluster Instance:
  - db.t3.medium instance class
  - Same engine and version as the cluster
  - DB subnet group for high availability

## Usage

Follow the instructions in the main README.md file to deploy this configuration.

Note: The default configuration uses "foo" as the username and "must_be_eight_characters" as the password. For production use, you should change these values and store them securely.