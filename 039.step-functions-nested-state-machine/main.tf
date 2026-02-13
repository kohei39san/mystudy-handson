# ===== Data Sources =====
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# ===== IAM Role for Lambda Functions =====
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-${var.environment}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_execution_role.name
}

# ===== Lambda Function Archives =====
data "archive_file" "parent_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/parent_lambda.py"
  output_path = "${path.module}/.terraform/archives/parent_lambda.zip"
}

data "archive_file" "child_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/child_lambda.py"
  output_path = "${path.module}/.terraform/archives/child_lambda.zip"
}

# ===== Lambda Functions =====
resource "aws_lambda_function" "parent_lambda" {
  filename         = data.archive_file.parent_lambda_zip.output_path
  function_name    = "${var.project_name}-${var.environment}-parent-lambda"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "parent_lambda.lambda_handler"
  source_code_hash = data.archive_file.parent_lambda_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory_size

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }
}

resource "aws_lambda_function" "child_lambda" {
  filename         = data.archive_file.child_lambda_zip.output_path
  function_name    = "${var.project_name}-${var.environment}-child-lambda"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "child_lambda.lambda_handler"
  source_code_hash = data.archive_file.child_lambda_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory_size

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }
}

# ===== CloudWatch Log Groups =====
resource "aws_cloudwatch_log_group" "parent_lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.parent_lambda.function_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "child_lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.child_lambda.function_name}"
  retention_in_days = 7
}

# ===== IAM Role for Step Functions =====
resource "aws_iam_role" "step_functions_execution_role" {
  name = "${var.project_name}-${var.environment}-sfn-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

# Policy to allow Step Functions to invoke Lambda
resource "aws_iam_role_policy" "step_functions_lambda_policy" {
  name = "${var.project_name}-${var.environment}-sfn-lambda-policy"
  role = aws_iam_role.step_functions_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          aws_lambda_function.parent_lambda.arn,
          aws_lambda_function.child_lambda.arn
        ]
      }
    ]
  })
}

# Policy to allow parent state machine to start child state machine
resource "aws_iam_role_policy" "step_functions_states_policy" {
  name = "${var.project_name}-${var.environment}-sfn-states-policy"
  role = aws_iam_role.step_functions_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution",
          "states:DescribeExecution",
          "states:StopExecution"
        ]
        Resource = [
          aws_sfn_state_machine.child_state_machine.arn,
          "${aws_sfn_state_machine.child_state_machine.arn}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "events:PutTargets",
          "events:PutRule",
          "events:DescribeRule"
        ]
        Resource = [
          "arn:aws:events:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule"
        ]
      }
    ]
  })
}

# ===== CloudWatch Logs for Step Functions =====
resource "aws_cloudwatch_log_group" "child_state_machine_logs" {
  name              = "/aws/vendedlogs/states/${var.project_name}-${var.environment}-child-sfn"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "parent_state_machine_logs" {
  name              = "/aws/vendedlogs/states/${var.project_name}-${var.environment}-parent-sfn"
  retention_in_days = 7
}

# ===== Step Functions State Machines =====
# Child State Machine
resource "aws_sfn_state_machine" "child_state_machine" {
  name     = "${var.project_name}-${var.environment}-child-sfn"
  role_arn = aws_iam_role.step_functions_execution_role.arn

  definition = templatefile("${path.module}/asl/child_state_machine.json", {
    child_lambda_function_arn = aws_lambda_function.child_lambda.arn
  })

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.child_state_machine_logs.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }

  type = "STANDARD"
}

# Parent State Machine
resource "aws_sfn_state_machine" "parent_state_machine" {
  name     = "${var.project_name}-${var.environment}-parent-sfn"
  role_arn = aws_iam_role.step_functions_execution_role.arn

  definition = templatefile("${path.module}/asl/parent_state_machine.json", {
    parent_lambda_function_arn = aws_lambda_function.parent_lambda.arn
    child_state_machine_arn    = aws_sfn_state_machine.child_state_machine.arn
  })

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.parent_state_machine_logs.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }

  type = "STANDARD"
}
