resource "random_password" "opensearch_master" {
  length           = 16
  special          = true
  override_special = "!#$%^&*()-_=+[]{}<>:?"
  min_special      = 1
  min_numeric      = 1
  min_upper        = 1
  min_lower        = 1
}

resource "aws_opensearch_domain" "vector_store" {
  domain_name    = "${var.project_name}-vectors"
  engine_version = "OpenSearch_2.9"

  cluster_config {
    instance_type          = var.opensearch_instance_type
    instance_count         = 1
    zone_awareness_enabled = false
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
    volume_type = "gp3"
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  advanced_options = {
    "rest.action.multi.allow_explicit_index" = "true"
  }

  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "admin"
      master_user_password = random_password.opensearch_master.result
    }
  }

  tags = {
    Name = "${var.project_name}-vectors"
  }
}
