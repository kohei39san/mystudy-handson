variable "github_repository" {
  description = "GitHub repository pattern to allow access from (e.g., 'repo:organization/repository:ref:refs/heads/main')"
  type        = string
  default     = "repo:organization/repository:*"
}

variable "environment" {
  description = "Environment name for tagging"
  type        = string
  default     = "dev"
}