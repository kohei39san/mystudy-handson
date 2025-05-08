output "redmine_public_ip" {
  description = "Public IP address of the Redmine instance"
  value       = aws_instance.redmine.public_ip
}

output "redmine_public_dns" {
  description = "Public DNS name of the Redmine instance"
  value       = aws_instance.redmine.public_dns
}

output "redmine_http_url" {
  description = "HTTP URL to access Redmine"
  value       = "http://${aws_instance.redmine.public_dns}"
}

output "ssh_command" {
  description = "SSH command to connect to the Redmine instance"
  value       = local.is_bitnami ? "ssh bitnami@${aws_instance.redmine.public_dns}" : "ssh ec2-user@${aws_instance.redmine.public_dns}"
}

output "redmine_ami_type" {
  description = "Type of AMI used for the Redmine instance"
  value       = local.is_bitnami ? "Bitnami Redmine AMI" : "Amazon Linux 2 (Manual Redmine installation required)"
}

output "redmine_ami_id" {
  description = "AMI ID used for the Redmine instance"
  value       = aws_instance.redmine.ami
}

output "security_note" {
  description = "Security reminder"
  value       = "Remember to change default passwords and consider setting up HTTPS for secure access."
}