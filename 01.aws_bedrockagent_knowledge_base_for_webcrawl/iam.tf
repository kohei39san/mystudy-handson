data "aws_iam_policy_document" "bedrock_knowledge_base_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "bedrock_knowledge_base" {
  statement {
    actions = [
      "es:ESHttpDelete",
      "es:ESHttpGet",
      "es:ESHttpHead",
      "es:ESHttpPost",
      "es:ESHttpPut"
    ]
    resources = [
      "${aws_opensearch_domain.knowledge_base.arn}/*"
    ]
  }
}

resource "aws_iam_role" "bedrock_knowledge_base" {
  name               = "bedrock-knowledge-base-role"
  assume_role_policy = data.aws_iam_policy_document.bedrock_knowledge_base_assume_role.json
}

resource "aws_iam_role_policy" "bedrock_knowledge_base" {
  name   = "bedrock-knowledge-base-policy"
  role   = aws_iam_role.bedrock_knowledge_base.id
  policy = data.aws_iam_policy_document.bedrock_knowledge_base.json
}
