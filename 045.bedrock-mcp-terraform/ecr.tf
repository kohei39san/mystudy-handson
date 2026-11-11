resource "aws_ecr_repository" "agent" {
  name                 = "${local.name_prefix}-agent"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource "docker_image" "agent" {
  name = "${aws_ecr_repository.agent.repository_url}:${var.agent_image_tag}"

  build {
    context    = path.module
    dockerfile = "Dockerfile"
    platform   = "linux/amd64"
  }

  triggers = {
    dockerfile_hash   = filesha256("${path.module}/Dockerfile")
    requirements_hash = filesha256("${path.module}/requirements-agent.txt")
    application_hash  = filesha256("${path.module}/agentcore_app/main.py")
  }
}

resource "docker_registry_image" "agent" {
  name          = docker_image.agent.name
  keep_remotely = true

  depends_on = [aws_ecr_repository.agent]
}