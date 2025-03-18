variable "aws_tags" {
  type    = map(string)
  default = {}
}
variable "github_repository" {
  description = "GitHub repository in format 'owner/repo'"
  type        = string
}
