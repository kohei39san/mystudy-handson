resource "aws_cloudformation_stack" "amazon_q_developer_slack" {
  name = "amazon-q-developer-in-slack"

  template_body = file("${path.module}/src/cfn/template.yaml")

  parameters = {
    SlackWorkspaceId = var.slack_workspace_id
    SlackChannelId   = var.slack_channel_id
    SlackChannelName = var.slack_channel_name
  }

  capabilities = ["CAPABILITY_NAMED_IAM"]

  tags = {
    Name        = "Amazon Q Developer in Slack"
    Environment = var.environment
    Terraform   = "true"
  }
}