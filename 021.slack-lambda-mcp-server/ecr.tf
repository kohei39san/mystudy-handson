# ECR リポジトリの作成
resource "aws_ecr_repository" "mcp_server_repo" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = var.ecr_repository_name
    Environment = "production"
    Project     = var.project_name
  }
}

# ECR リポジトリのライフサイクルポリシー
resource "aws_ecr_lifecycle_policy" "mcp_server_repo_policy" {
  repository = aws_ecr_repository.mcp_server_repo.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the last 5 images"
        selection = {
          tagStatus     = "any"
          countType     = "imageCountMoreThan"
          countNumber   = 5
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Docker イメージのビルドとプッシュ
resource "null_resource" "docker_build_push" {
  triggers = {
    dockerfile_hash = filemd5("${path.module}/../src/021.slack-lambda-mcp-server/docker/Dockerfile")
    requirements_hash = filemd5("${path.module}/../src/021.slack-lambda-mcp-server/docker/requirements.txt")
    lambda_function_hash = filemd5("${path.module}/../scripts/021.slack-lambda-mcp-server/py/lambda_function.py")
  }

  provisioner "local-exec" {
    command = <<EOF
      # AWS ECR 認証トークンを取得
      aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com
      
      # Lambda 関数をコンテナディレクトリにコピー
      cp ${path.module}/../scripts/021.slack-lambda-mcp-server/py/lambda_function.py ${path.module}/../src/021.slack-lambda-mcp-server/docker/
      
      # Docker イメージをビルド
      docker build -t ${aws_ecr_repository.mcp_server_repo.repository_url}:latest ${path.module}/../src/021.slack-lambda-mcp-server/docker/
      
      # Docker イメージをプッシュ
      docker push ${aws_ecr_repository.mcp_server_repo.repository_url}:latest
    EOF
  }

  depends_on = [
    aws_ecr_repository.mcp_server_repo
  ]
}

# Docker プロバイダーの設定
provider "docker" {
  registry_auth {
    address  = "${local.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
    username = "AWS"
    password = data.aws_ecr_authorization_token.token.password
  }
}

# ECR 認証トークンの取得
data "aws_ecr_authorization_token" "token" {}