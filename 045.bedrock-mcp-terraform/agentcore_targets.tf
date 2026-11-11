resource "aws_bedrockagentcore_gateway_target" "github" {
  gateway_identifier = aws_bedrockagentcore_gateway.this.gateway_id
  name               = "github-mcp"

  credential_provider_configuration {
    oauth {
      provider_arn = aws_bedrockagentcore_oauth2_credential_provider.github.credential_provider_arn
      scopes       = ["repo", "read:org"]
    }
  }

  target_configuration {
    mcp {
      mcp_server {
        endpoint = var.github_mcp_endpoint
      }
    }
  }
}