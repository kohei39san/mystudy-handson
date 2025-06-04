output "slack_channel_configuration_arn" {
  description = "ARN of the Slack Channel Configuration"
  value       = aws_cloudformation_stack.amazon_q_developer_slack.outputs["SlackChannelConfigurationArn"]
}

output "iam_role_arn" {
  description = "ARN of the IAM Role for Amazon Q Developer in Slack"
  value       = aws_cloudformation_stack.amazon_q_developer_slack.outputs["IAMRoleArn"]
}