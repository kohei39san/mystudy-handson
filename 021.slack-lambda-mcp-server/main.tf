provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------------------------------------------------------------------
# S3 Bucket for Data Source
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_s3_bucket" "data_source" {
  bucket = var.s3_bucket_name
  force_destroy = true

  tags = {
    Name        = "Slack MCP Data Source"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_ownership_controls" "data_source" {
  bucket = aws_s3_bucket.data_source.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "data_source" {
  depends_on = [aws_s3_bucket_ownership_controls.data_source]
  bucket = aws_s3_bucket.data_source.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "data_source" {
  bucket = aws_s3_bucket.data_source.id
  versioning_configuration {
    status = "Enabled"
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# DynamoDB Table for Conversation History
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_dynamodb_table" "conversations" {
  name           = var.dynamodb_table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "conversationId"
  range_key      = "messageId"

  attribute {
    name = "conversationId"
    type = "S"
  }

  attribute {
    name = "messageId"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name        = "Slack MCP Conversations"
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# OpenSearch Domain
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_opensearch_domain" "vector_store" {
  domain_name    = var.opensearch_domain_name
  engine_version = "OpenSearch_2.11"

  cluster_config {
    instance_type = "t3.small.search"
    instance_count = 1
    zone_awareness_enabled = false
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

  domain_endpoint_options {
    enforce_https = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  advanced_security_options {
    enabled = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = var.opensearch_master_user
      master_user_password = var.opensearch_master_password
    }
  }

  access_policies = <<CONFIG
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:${var.aws_region}:${data.aws_caller_identity.current.account_id}:domain/${var.opensearch_domain_name}/*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": ["${var.allowed_ip_range}"]
        }
      }
    }
  ]
}
CONFIG

  tags = {
    Name        = "Slack MCP Vector Store"
    Environment = var.environment
  }
}