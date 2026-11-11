resource "aws_bedrockagentcore_oauth2_credential_provider" "github" {
  credential_provider_vendor = "GithubOauth2"
  name                       = "${local.name_prefix}-github"

  oauth2_provider_config {
    github_oauth2_provider_config {
      client_id     = var.github_oauth_client_id
      client_secret = var.github_oauth_client_secret
    }
  }
}