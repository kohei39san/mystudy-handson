output "ssh_cmd" {
  description = "to access ec2 by ssh"
  value       = "ssh -i ${var.instance_private_key} ec2-user@${aws_instance.test_instance.public_ip}"
}

output "instance_public_key" {
  description = "instance public key"
  value       = var.instance_public_key
}

output "instance_private_key" {
  description = "instance private key"
  value       = var.instance_private_key
}

output "test_instance" {
  description = "test instance"
  value       = aws_instance.test_instance
}
