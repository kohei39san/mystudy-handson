resource "aws_opensearch_domain" "knowledge_base" {
  domain_name    = "webcrawl-opensearch"
  engine_version = var.opensearch_engine_version

  cluster_config {
    instance_type  = var.opensearch_instance_type
    instance_count = 1
    zone_awareness_config {
      availability_zone_count = 1
    }
    zone_awareness_enabled = false
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
    volume_type = "gp2"
  }
}

resource "aws_bedrockagent_knowledge_base" "webcrawl" {
  name            = var.knowledge_base_name
  role_arn        = aws_iam_role.bedrock_knowledge_base.arn
  description     = "Knowledge base for web crawling data"

  storage_configuration {
    type = "OPENSEARCH_SERVICE"
    opensearch_service_configuration {
      endpoint = aws_opensearch_domain.knowledge_base.endpoint
      index_name = "webcrawl-index"
      field_mapping {
        vector_field   = "vector"
        text_field     = "text"
        metadata_field = "metadata"
      }
    }
  }

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v1"
    }
  }

  data_source {
    name            = "webcrawl-data-source"
    data_source_configuration {
      type = "WEB_CRAWLER"
      web_crawler_configuration {
        urls {
          seed_url_configuration {
            web_crawler_mode = "SUBDOMAINS"
            seed_url         = "https://example.com"
          }
        }
      }
    }
  }
}
