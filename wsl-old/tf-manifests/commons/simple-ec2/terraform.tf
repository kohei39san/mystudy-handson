# tflint-ignore-file: terraform_required_providers, terraform_required_version
terraform {}

provider "aws" {
  default_tags {
    tags = merge(var.aws_tags, {
      Environment = "Development"
      Terraform   = "true"
    })
  }
}