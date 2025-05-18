output "role_arn" {
  description = "ARN of the created IAM Role for TFLint AWS Plugin"
  value       = aws_cloudformation_stack.tflint_readonly_oidc.outputs["RoleARN"]
}

output "instructions" {
  description = "Instructions for using the role in GitHub Actions"
  value       = aws_cloudformation_stack.tflint_readonly_oidc.outputs["Instructions"]
}