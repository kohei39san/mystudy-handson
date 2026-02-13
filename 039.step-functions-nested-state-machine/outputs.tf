output "parent_lambda_function_name" {
  description = "Name of the parent Lambda function"
  value       = aws_lambda_function.parent_lambda.function_name
}

output "parent_lambda_function_arn" {
  description = "ARN of the parent Lambda function"
  value       = aws_lambda_function.parent_lambda.arn
}

output "child_lambda_function_name" {
  description = "Name of the child Lambda function"
  value       = aws_lambda_function.child_lambda.function_name
}

output "child_lambda_function_arn" {
  description = "ARN of the child Lambda function"
  value       = aws_lambda_function.child_lambda.arn
}

output "parent_state_machine_arn" {
  description = "ARN of the parent Step Functions state machine"
  value       = aws_sfn_state_machine.parent_state_machine.arn
}

output "parent_state_machine_name" {
  description = "Name of the parent Step Functions state machine"
  value       = aws_sfn_state_machine.parent_state_machine.name
}

output "child_state_machine_arn" {
  description = "ARN of the child Step Functions state machine"
  value       = aws_sfn_state_machine.child_state_machine.arn
}

output "child_state_machine_name" {
  description = "Name of the child Step Functions state machine"
  value       = aws_sfn_state_machine.child_state_machine.name
}

output "execution_command" {
  description = "Command to execute the parent state machine"
  value       = <<-EOT
    aws stepfunctions start-execution \
      --state-machine-arn ${aws_sfn_state_machine.parent_state_machine.arn} \
      --input '{"initial_value": 10, "processing_type": "multiply"}' \
      --region ${var.aws_region}
  EOT
}
