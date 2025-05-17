# CloudFormationスタックのデプロイ
resource "aws_cloudformation_stack" "bedrock" {
  name          = "${var.project_name}-bedrock"
  template_body = file("${path.module}/../src/014.bedrock-webcrawler/cfn/bedrock-stack.yaml")
  iam_role_arn  = aws_iam_role.cloudformation.arn
  capabilities  = ["CAPABILITY_IAM"]

  parameters = {
    ProjectName        = var.project_name
    BedrockRoleArn     = aws_iam_role.bedrock_opensearch.arn
    OpenSearchArn      = aws_opensearch_domain.vector_store.arn
    OpenSearchEndpoint = aws_opensearch_domain.vector_store.endpoint
    AwsRegion          = var.aws_region
    CrawlingUrl        = var.crawling_url
    BedrockModelArn    = var.bedrock_model_arn
    CrawlerScope       = var.crawler_scope
  }

  depends_on = [
    aws_opensearch_domain.vector_store,
    aws_iam_role.bedrock_opensearch,
    opensearch_index.blog_index
  ]
}
