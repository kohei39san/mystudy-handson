output "rds_iam_role_arn" {
  description = "ARN of the RDS IAM role"
  value       = aws_iam_role.rds_iam_role.arn
}

output "rds_iam_role_name" {
  description = "Name of the RDS IAM role"
  value       = aws_iam_role.rds_iam_role.name
}

output "postgres_iam_user_arn" {
  description = "ARN of the PostgreSQL IAM user"
  value       = aws_iam_user.postgres_iam_user.arn
}

output "postgres_iam_user_name" {
  description = "Name of the PostgreSQL IAM user"
  value       = aws_iam_user.postgres_iam_user.name
}

output "rds_connect_policy_arn" {
  description = "ARN of the RDS connect policy"
  value       = aws_iam_policy.rds_connect_policy.arn
}

output "aws_account_id" {
  description = "Current AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "Current AWS region"
  value       = data.aws_region.current.name
}