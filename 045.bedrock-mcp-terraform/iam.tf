data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "agentcore_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["bedrock-agentcore.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "agentcore_runtime" {
  name               = "${local.name_prefix}-agentcore-runtime"
  assume_role_policy = data.aws_iam_policy_document.agentcore_assume_role.json
}

resource "aws_iam_role" "agentcore_gateway" {
  name               = "${local.name_prefix}-agentcore-gateway"
  assume_role_policy = data.aws_iam_policy_document.agentcore_assume_role.json
}

resource "aws_iam_role" "api_adapter" {
  name               = "${local.name_prefix}-api-adapter"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "api_adapter" {
  statement {
    effect    = "Allow"
    actions   = ["bedrock-agentcore:InvokeAgentRuntime"]
    resources = [aws_bedrockagentcore_agent_runtime.this.agent_runtime_arn]
  }

  statement {
    effect    = "Allow"
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${local.name_prefix}-api-adapter:*"]
  }
}

resource "aws_iam_role_policy" "api_adapter" {
  name   = "${local.name_prefix}-api-adapter"
  role   = aws_iam_role.api_adapter.id
  policy = data.aws_iam_policy_document.api_adapter.json
}
