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

# Generic Terraform rules for all providers
rule "terraform_required_version" {
  enabled = true
}

rule "terraform_typed_variables" {
  enabled = true
}

rule "terraform_unused_declarations" {
  enabled = true
}

rule "terraform_deprecated_interpolation" {
  enabled = true
}

rule "terraform_naming_convention" {
  enabled = true
  format = "snake_case"
}