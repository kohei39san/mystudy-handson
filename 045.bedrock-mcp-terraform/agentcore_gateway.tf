resource "aws_bedrockagentcore_gateway" "this" {
  authorizer_type = "NONE"
  name            = var.agentcore_gateway_name
  role_arn        = aws_iam_role.agentcore_gateway.arn
  protocol_type   = "MCP"

  tags = local.tags
}