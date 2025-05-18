# AWS ReadOnly OIDC for TFLint

This module sets up GitHub OIDC integration with AWS to allow TFLint to use the AWS plugin with deep_check enabled. The setup uses assume_role functionality to securely access AWS resources without storing long-lived credentials.

## Overview

The solution consists of:

1. CloudFormation stack that creates:
   - GitHub OIDC provider in AWS IAM
   - IAM Role with ReadOnlyAccess policy
   - Trust relationship between GitHub Actions and AWS

2. Terraform configuration to deploy the CloudFormation stack

3. GitHub Actions workflow that:
   - Uses the OIDC provider to assume the IAM role
   - Runs TFLint with AWS plugin enabled

## Setup Instructions

### 1. Deploy the AWS Resources

1. Clone this repository
2. Navigate to the `020.aws-readonly-oidc` directory
3. Create a `terraform.tfvars` file based on the example:
   ```
   cp terraform.tfvars.example terraform.tfvars
   ```
4. Edit the `terraform.tfvars` file with your GitHub organization and repository name
5. Initialize and apply the Terraform configuration:
   ```
   terraform init
   terraform apply
   ```
6. Note the output `github_actions_role_arn` value

### 2. Configure GitHub Repository

1. In your GitHub repository, go to Settings > Secrets and variables > Actions
2. Add a new repository secret:
   - Name: `AWS_ROLE_ARN`
   - Value: The Role ARN from the Terraform output (e.g., `arn:aws:iam::123456789012:role/github-actions-tflint-readonly-your-repository-name`)

### 3. How It Works

The GitHub Actions workflow:
1. Authenticates with AWS using OIDC
2. Assumes the IAM role with ReadOnlyAccess permissions
3. Runs TFLint with the AWS plugin enabled and deep_check set to true
4. If the AWS role assumption fails, falls back to running TFLint without the AWS plugin

The AWS plugin for TFLint performs deep validation of your Terraform code against actual AWS service APIs, which helps catch issues that basic validation might miss.

## Security Considerations

- The IAM role has only ReadOnlyAccess permissions
- No AWS credentials are stored in GitHub
- The trust relationship is scoped to your specific GitHub repository
- The OIDC token is short-lived and automatically rotated

## Troubleshooting

If TFLint is not using the AWS plugin:

1. Check that the `AWS_ROLE_ARN` secret is correctly set in your GitHub repository
2. Verify that the IAM role exists and has the correct trust relationship
3. Ensure the GitHub Actions workflow has the `id-token: write` permission
4. Check the GitHub Actions logs for any authentication errors