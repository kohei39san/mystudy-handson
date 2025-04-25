resource "aws_bedrockagent_knowledge_base" "webcrawl" {
  name     = var.knowledge_base_name
  role_arn = aws_iam_role.bedrock_knowledge_base.arn

  knowledge_base_configuration {
    type = "VECTOR"

    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/amazon.titan-embed-text-v1"
    }
  }

  storage_configuration {
    type = "OPENSEARCH"

    opensearch_configuration {
      domain_arn     = aws_opensearch_domain.webcrawl.arn
      index_name     = "webcrawl-index"
      vector_field   = "vector"
      text_field     = "text"
      metadata_field = "metadata"
    }
  }

  data_source {
    name     = "webcrawl-datasource"
    data_deletion_policy = "RETAIN"

    data_source_configuration {
      type = "WEB_CRAWLER"

      web_crawler_configuration {
        urls = ["https://example.com"]  # Update with target URLs
        crawl_depth = 2
      }
    }
  }
}

resource "aws_opensearch_domain" "webcrawl" {
  domain_name           = "webcrawl-domain"
  engine_version        = "OpenSearch_2.11"

  cluster_config {
    instance_type  = var.opensearch_instance_type
    instance_count = var.instance_count
  }

  ebs_options {
    ebs_enabled = true
    volume_size = var.ebs_volume_size
    volume_type = var.ebs_volume_type
  }
}

data "aws_region" "current" {}
