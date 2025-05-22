# OpenSearch インデックスの作成
resource "opensearch_index" "kb_index" {
  name               = "bedrock-kb-index"
  number_of_shards   = 1
  number_of_replicas = 1
  
  # OpenSearch ドメインが作成された後に実行
  depends_on = [
    aws_opensearch_domain.kb_opensearch,
    aws_opensearch_domain_policy.kb_opensearch_policy
  ]
  
  # インデックスの設定とマッピング
  body = file("${path.module}/../src/021.slack-lambda-mcp-server/opensearch-index.json")
}

# OpenSearch プロバイダーの設定
provider "opensearch" {
  url                   = "https://${aws_opensearch_domain.kb_opensearch.endpoint}"
  aws_region            = var.aws_region
  aws_assume_role_arn   = aws_iam_role.opensearch_master_user_role.arn
  
  # AWS 認証情報を使用
  aws_profile           = null
  aws_access_key        = null
  aws_secret_key        = null
  
  # 自己署名証明書を許可
  insecure              = true
  
  # OpenSearch ドメインが作成された後に実行
  depends_on = [
    aws_opensearch_domain.kb_opensearch,
    aws_opensearch_domain_policy.kb_opensearch_policy
  ]
}