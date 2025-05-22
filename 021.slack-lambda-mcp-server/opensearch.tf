# OpenSearch ドメインの作成
resource "aws_opensearch_domain" "kb_opensearch" {
  domain_name    = var.opensearch_domain_name
  engine_version = "OpenSearch_2.5"

  # 最小コストの構成
  cluster_config {
    instance_type            = var.opensearch_instance_type
    instance_count           = var.opensearch_instance_count
    dedicated_master_enabled = false
    zone_awareness_enabled   = false
  }

  # EBS ボリューム設定
  ebs_options {
    ebs_enabled = true
    volume_size = var.opensearch_ebs_volume_size
    volume_type = "gp3"
  }

  # 暗号化設定
  encrypt_at_rest {
    enabled = true
  }

  # ノード間通信の暗号化
  node_to_node_encryption {
    enabled = true
  }

  # HTTPS 強制
  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  # IAM認証を使用
  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = false
    master_user_options {
      master_user_arn = aws_iam_role.opensearch_master_user_role.arn
    }
  }

  tags = {
    Name        = var.opensearch_domain_name
    Environment = "production"
    Project     = var.project_name
  }
}

# OpenSearch マスターユーザーロール
resource "aws_iam_role" "opensearch_master_user_role" {
  name = "opensearch-master-user-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.account_id}:root"
        }
      }
    ]
  })

  tags = {
    Name    = "opensearch-master-user-role"
    Project = var.project_name
  }
}

# OpenSearch ドメインポリシー
resource "aws_opensearch_domain_policy" "kb_opensearch_policy" {
  domain_name = aws_opensearch_domain.kb_opensearch.domain_name

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = [
            aws_iam_role.opensearch_master_user_role.arn,
            aws_iam_role.bedrock_opensearch_role.arn,
            aws_iam_role.mcp_server_role.arn
          ]
        }
        Action   = "es:*"
        Resource = "${aws_opensearch_domain.kb_opensearch.arn}/*"
      }
    ]
  })
}