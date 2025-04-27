resource "aws_opensearch_domain" "bedrock_knowledge_base" {
  domain_name    = "bedrock-knowledge-base"
  engine_version = var.opensearch_version

  cluster_config {
    instance_type  = var.opensearch_instance_type
    instance_count = 1
  }

  ebs_options {
    ebs_enabled = true
    volume_size = var.storage_size
  }

  node_to_node_encryption {
    enabled = true
  }

  encrypt_at_rest {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
}

resource "aws_bedrockagent_knowledge_base" "web_crawl" {
  name = "web-crawl-knowledge-base"
  role_arn = aws_iam_role.bedrock_knowledge_base.arn

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}"
    }
  }

  storage_configuration {
    type = "OPENSEARCH_SERVERLESS"
    opensearch_serverless_configuration {
      collection_arn    = aws_opensearch_domain.bedrock_knowledge_base.arn
      vector_index_name = "bedrock-knowledge-base-index"
      field_mapping {
        vector_field   = "vector"
        text_field     = "text"
        metadata_field = "metadata"
      }
    }
  }
}

resource "aws_bedrockagent_data_source" "web_crawler" {
  name             = "web-crawler-source"
  knowledge_base_id = aws_bedrockagent_knowledge_base.web_crawl.id
  data_source_configuration {
    type = "WEB_CRAWLER"
    web_crawler_configuration {
      urls = var.web_crawler_urls
      crawling_configuration {
        site_maps = []
        url_inclusion_patterns = ["^https://example.com/.*"]
        url_exclusion_patterns = []
      }
    }
  }
}
