locals {
  name_prefix = "${var.project_name}-${var.environment}"

  api_authorization_type = var.api_authorizer_type == "AWS_IAM" ? "AWS_IAM" : "NONE"

  tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}
