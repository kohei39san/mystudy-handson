resource "aws_bedrockagentcore_agent_runtime" "this" {
  agent_runtime_name = var.agentcore_runtime_name
  role_arn           = aws_iam_role.agentcore_runtime.arn

  agent_runtime_artifact {
    container_configuration {
      container_uri = docker_registry_image.agent.name
    }
  }

  environment_variables = {
    AGENTCORE_GATEWAY_URL = aws_bedrockagentcore_gateway.this.gateway_url
  }

  network_configuration {
    network_mode = "PUBLIC"
  }

  tags = local.tags
}