resource "aws_cloudformation_stack" "tflint_readonly_oidc" {
  name = "tflint-aws-readonly-oidc"

  template_body = file("${path.module}/../src/020.aws-readonly-oidc/cfn/stack.yaml")

  parameters = {
    GitHubRepository = var.github_repository
  }

  capabilities = ["CAPABILITY_NAMED_IAM"]

  tags = {
    Name        = "TFLint AWS Plugin ReadOnly Role"
    Environment = var.environment
    Terraform   = "true"
  }
}