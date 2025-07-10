# Minikube with OpenSearch and Prometheus Setup

This Terraform configuration creates an EC2 instance with Minikube, OpenSearch, and Prometheus installed, with the following resources:

## Resource Configuration

### Network Resources
- VPC with CIDR block 10.0.0.0/16
- Public subnet
- Internet Gateway
- Route Table with routes to the Internet Gateway
- Security Group for the instance

### Compute Resources
- EC2 instance with:
  - Installation scripts for Docker and Minikube
  - Bootstrap configuration for setting up the environment

### Kubernetes Resources
- OpenSearch deployment configurations:
  - OpenSearch leader node
  - OpenSearch data nodes
  - Snapshot repository registration
  - SLM (Snapshot Lifecycle Management) configuration

### IAM Resources
- IAM role and policies for the EC2 instance

## Usage

Follow the instructions in the main README.md file to deploy this configuration.

After deployment, you can access:
- OpenSearch dashboard
- Prometheus monitoring interface

Refer to the documentation in the `docs` directory for additional information.