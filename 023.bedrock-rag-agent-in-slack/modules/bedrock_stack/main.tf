terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_cloudformation_stack" "bedrock_stack" {
  name          = "${var.main_stack_name}-bedrock-stack"
  template_body = file("${path.module}/../../../src/023.bedrock-rag-agent-in-slack/cfn/bedrock-template.yaml")
  capabilities  = ["CAPABILITY_NAMED_IAM"]

  parameters = {
    MainStackName            = var.main_stack_name
    BedrockModelId           = var.bedrock_model_id
    BedrockOpensearchRoleArn = var.bedrock_opensearch_role_arn
    EmbeddingModelId         = var.embedding_model_id
    DomainEndpoint           = var.opensearch_endpoint
    KnowledgeBaseBucketArn   = var.knowledge_base_bucket_arn
    OpensearchDomainArn      = var.opensearch_domain_arn
  }

  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}