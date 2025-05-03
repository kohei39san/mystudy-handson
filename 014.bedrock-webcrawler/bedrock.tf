# CloudFormationスタックのデプロイ
resource "aws_cloudformation_stack" "bedrock" {
  name          = "${var.project_name}-bedrock"
  template_body = file("${path.module}/../src/014.bedrock-webcrawler/bedrock-stack.yaml")
  capabilities  = ["CAPABILITY_IAM"]

  parameters = {
    ProjectName        = var.project_name
    BedrockRoleArn     = aws_iam_role.bedrock_opensearch.arn
    OpenSearchArn      = aws_opensearch_domain.vector_store.arn
    OpenSearchEndpoint = aws_opensearch_domain.vector_store.endpoint
    AwsRegion          = var.aws_region
    CrawlingUrl       = var.crawling_url
  }

  depends_on = [
    aws_opensearch_domain.vector_store,
    aws_iam_role.bedrock_opensearch
  ]
}
