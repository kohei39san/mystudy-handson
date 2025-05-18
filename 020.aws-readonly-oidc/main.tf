terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Deploy CloudFormation stack for GitHub OIDC and IAM Role
resource "aws_cloudformation_stack" "github_oidc" {
  name         = "github-oidc-tflint-readonly"
  capabilities = ["CAPABILITY_NAMED_IAM"]
  template_body = file("${path.module}/../src/020.aws-readonly-oidc/cfn/stack.yaml")
  
  parameters = {
    GitHubOrg       = var.github_org
    GitHubRepository = var.github_repository
  }

  tags = {
    Name        = "GitHub OIDC for TFLint"
    Environment = var.environment
    Project     = "020.aws-readonly-oidc"
  }
}

# Output the Role ARN for use in GitHub Actions
output "github_actions_role_arn" {
  description = "ARN of the IAM Role for GitHub Actions"
  value       = aws_cloudformation_stack.github_oidc.outputs["GitHubActionsRoleARN"]
}

output "oidc_provider_arn" {
  description = "ARN of the GitHub OIDC Provider"
  value       = aws_cloudformation_stack.github_oidc.outputs["OIDCProviderARN"]
}