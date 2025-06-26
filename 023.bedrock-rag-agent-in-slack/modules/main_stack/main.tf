terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_cloudformation_stack" "main_stack" {
  name          = "${var.project_name}-main-stack"
  template_body = file("${path.module}/../../src/cfn/template.yaml")
  capabilities  = ["CAPABILITY_NAMED_IAM"]

  parameters = {
    SlackWorkspaceId       = var.slack_workspace_id
    SlackChannelId         = var.slack_channel_id
    SlackChannelName       = var.slack_channel_name
    ProjectName            = var.project_name
    CallerIdentityArn      = data.aws_caller_identity.current.arn
    OpenSearchInstanceType = var.opensearch_instance_type
  }

  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}