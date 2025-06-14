plugin "aws" {
  enabled = true
  version = "0.40.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
  deep_check = true
}

rule "aws_resource_missing_tags" {
  enabled = true
  tags = ["Terraform", "Environment"]
}

rule "aws_instance_previous_type" {
  enabled = true
}

rule "aws_instance_invalid_type" {
  enabled = true
}

rule "aws_instance_invalid_ami" {
  enabled = true
}