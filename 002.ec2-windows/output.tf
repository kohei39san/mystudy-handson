output "windows_public_ip" {
  description = "windows_public_ip"
  value       = aws_instance.test_instance.public_ip
}

output "private_key" {
  description = "private_key"
  value       = var.instance_private_key
}