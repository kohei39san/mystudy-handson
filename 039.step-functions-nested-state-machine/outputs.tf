output "parent_lambda_function_name" {
  description = "Name of the parent Lambda function"
  value       = aws_cloudformation_stack.nested.outputs["ParentLambdaFunctionName"]
}

output "parent_lambda_function_arn" {
  description = "ARN of the parent Lambda function"
  value       = aws_cloudformation_stack.nested.outputs["ParentLambdaFunctionArn"]
}

output "child_lambda_function_name" {
  description = "Name of the child Lambda function"
  value       = aws_cloudformation_stack.nested.outputs["ChildLambdaFunctionName"]
}

output "child_lambda_function_arn" {
  description = "ARN of the child Lambda function"
  value       = aws_cloudformation_stack.nested.outputs["ChildLambdaFunctionArn"]
}

output "parent_state_machine_arn" {
  description = "ARN of the parent Step Functions state machine"
  value       = aws_cloudformation_stack.nested.outputs["ParentStateMachineArn"]
}

output "parent_state_machine_name" {
  description = "Name of the parent Step Functions state machine"
  value       = aws_cloudformation_stack.nested.outputs["ParentStateMachineName"]
}

output "child_state_machine_arn" {
  description = "ARN of the child Step Functions state machine"
  value       = aws_cloudformation_stack.nested.outputs["ChildStateMachineArn"]
}

output "child_state_machine_name" {
  description = "Name of the child Step Functions state machine"
  value       = aws_cloudformation_stack.nested.outputs["ChildStateMachineName"]
}

output "execution_command" {
  description = "Command to execute the parent state machine"
  value       = <<-EOT
    aws stepfunctions start-execution \
      --state-machine-arn ${aws_cloudformation_stack.nested.outputs["ParentStateMachineArn"]} \
      --input '{"initial_value": 10, "processing_type": "multiply"}' \
      --region ${var.aws_region}
  EOT
}
