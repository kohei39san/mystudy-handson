resource "aws_cloudformation_stack" "nested" {
  name          = var.stack_name
  template_body = file("${path.module}/cfn/infrastructure.yaml")
  capabilities  = ["CAPABILITY_NAMED_IAM"]

  parameters = {
    ProjectName = var.project_name
    Environment = var.environment
  }
}
