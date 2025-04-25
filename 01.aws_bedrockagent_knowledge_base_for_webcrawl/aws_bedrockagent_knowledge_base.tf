resource "aws_opensearch_domain" "knowledge_base" {
  domain_name           = "bedrock-knowledge-base"
  engine_version        = "OpenSearch_2.11"

  cluster_config {
    instance_type          = var.opensearch_instance_type
    instance_count         = 1
    dedicated_master_count = 0
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }
}

resource "aws_bedrockagent_knowledge_base" "main" {
  name        = "webcrawl-knowledge-base"
  description = "Knowledge base for web crawling"
  role_arn    = aws_iam_role.bedrock_knowledge_base.arn

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = var.embedding_model_arn
    }
  }

  storage_configuration {
    type = "OPENSEARCH"
    opensearch_configuration {
      domain_arn     = aws_opensearch_domain.knowledge_base.arn
      index_name     = "bedrock-knowledge-index"
      field_mapping {
        vector_field   = "bedrock-knowledge-vector"
        text_field     = "text"
        metadata_field = "metadata"
      }
    }
  }

  data_source {
    name = "web-crawler"
    type = "WEB_CRAWLER"

    data_source_configuration {
      web_crawler_configuration {
        urls = ["https://example.com"] # Update with target URLs
      }
    }
  }
}
