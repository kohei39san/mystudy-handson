# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/bedrockagent_knowledge_base
resource "aws_bedrockagent_knowledge_base" "webcrawl" {
  name     = var.knowledge_base_name
  role_arn = aws_iam_role.bedrock_knowledge_base.arn

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
    }
  }

  storage_configuration {
    type = "OPENSEARCH"
    opensearch_configuration {
      domain_arn     = aws_opensearch_domain.knowledge_base.arn
      index_name     = "bedrock-knowledge-base-index"
      field_mapping {
        vector_field   = "bedrock-knowledge-base-vector"
        text_field     = "text"
        metadata_field = "metadata"
      }
    }
  }

  data_source_configuration {
    type = "WEBCRAWL"

    web_crawl_configuration {
      urls = ["https://example.com"] # Replace with target URLs
      crawl_depth = 2

      schedule {
        schedule_expression = "cron(0 12 * * ? *)" # Daily at 12:00 UTC
      }
    }
  }
}

# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/opensearch_domain
resource "aws_opensearch_domain" "knowledge_base" {
  domain_name    = "${var.knowledge_base_name}-opensearch"
  engine_version = var.opensearch_version

  cluster_config {
    instance_type = var.opensearch_instance_type
  }

  # Cost optimization settings
  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 10
  }

  advanced_security_options {
    enabled = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "admin"
      master_user_password = "ChangeMe123!" # Use AWS Secrets Manager in production
    }
  }
}
