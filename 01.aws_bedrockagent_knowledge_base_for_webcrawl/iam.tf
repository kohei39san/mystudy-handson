data "aws_iam_policy_document" "bedrock_agent_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "bedrock_knowledge_base" {
  name               = "BedrockKnowledgeBaseRole"
  assume_role_policy = data.aws_iam_policy_document.bedrock_agent_assume_role.json
}

resource "aws_iam_role_policy_attachment" "bedrock_knowledge_base" {
  role       = aws_iam_role.bedrock_knowledge_base.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
}

data "aws_iam_policy_document" "opensearch_access" {
  statement {
    actions = [
      "es:ESHttpPost",
      "es:ESHttpPut",
      "es:ESHttpGet"
    ]
    resources = [
      "${aws_opensearch_domain.bedrock_knowledge_base.arn}/*"
    ]
  }
}

resource "aws_iam_role_policy" "opensearch_access" {
  name   = "OpenSearchAccessPolicy"
  role   = aws_iam_role.bedrock_knowledge_base.id
  policy = data.aws_iam_policy_document.opensearch_access.json
}
