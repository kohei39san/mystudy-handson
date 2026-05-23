resource "aws_cloudformation_stack" "hello_world_stack" {
  name          = var.lambda_cfnstack_name
  template_body = file("lambda.yaml")
  capabilities  = ["CAPABILITY_NAMED_IAM"]
  parameters = {
    FunctionName = var.lambda_function_name
  }
}