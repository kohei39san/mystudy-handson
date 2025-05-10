output "redmine_public_ip" {
  description = "Public IP address of the Redmine instance"
  value       = aws_instance.redmine_instance.public_ip
}

output "redmine_url" {
  description = "URL to access Redmine"
  value       = "http://${aws_instance.redmine_instance.public_ip}"
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ${var.private_key_path} ec2-user@${aws_instance.redmine_instance.public_ip}"
}
}