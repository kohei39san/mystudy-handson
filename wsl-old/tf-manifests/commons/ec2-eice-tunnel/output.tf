output "instance" {
  description = "ec2"
  value       = aws_instance.instance
}

output "private_key" {
  description = "private key"
  value       = var.instance_private_key
}
