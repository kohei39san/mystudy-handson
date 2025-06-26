terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

# Create Lambda function zip file
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../lambda_source/github_to_s3_sync"
  output_path = "${path.module}/../../../../github-to-s3-sync.zip"
}

resource "aws_cloudformation_stack" "lambda_stack" {
  name          = "${var.main_stack_name}-lambda-stack"
  template_body = file("${path.module}/../../src/cfn/lambda-template.yaml")
  capabilities  = ["CAPABILITY_NAMED_IAM"]

  parameters = {
    MainStackName           = var.main_stack_name
    GitHubRepositoryUrl     = var.github_repository_url
    GitHubPAT               = var.github_pat
    GitHubUsername          = var.github_username
    ScheduleExpression      = var.schedule_expression
    KnowledgeBaseBucketArn  = var.knowledgebase_bucket_arn
    KnowledgeBaseBucketName = var.knowledgebase_bucket_name
    KnowledgeBaseId         = var.knowledgebase_id
    DataSourceId            = var.datasource_id

  }

  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}

# Update Lambda function code after deployment
resource "null_resource" "update_lambda_code" {
  depends_on = [aws_cloudformation_stack.lambda_stack]

  triggers = {
    lambda_zip_hash = data.archive_file.lambda_zip.output_base64sha256
  }

  provisioner "local-exec" {
    command = <<-EOT
      aws lambda update-function-code --function-name ${aws_cloudformation_stack.lambda_stack.outputs["LambdaFunctionArn"]} --zip-file fileb://${path.module}/../../../../github-to-s3-sync.zip
      aws lambda wait function-updated-v2 --function-name ${aws_cloudformation_stack.lambda_stack.outputs["LambdaFunctionArn"]}
      aws lambda invoke --function-name ${aws_cloudformation_stack.lambda_stack.outputs["LambdaFunctionArn"]} --payload '{}' --query 'StatusCode' "${path.module}/../../../../lambda_output.json"
    EOT
  }
}

resource "null_resource" "invoke_lambda" {
  depends_on = [null_resource.update_lambda_code]

  triggers = {
    lambda_arn = aws_cloudformation_stack.lambda_stack.outputs["LambdaFunctionArn"]
  }

  provisioner "local-exec" {
    command = <<-EOT
      aws lambda invoke --function-name ${self.triggers.lambda_arn} --payload '{}' --query 'StatusCode' ${path.module}/../../../../lambda_output.json
    EOT
  }
}