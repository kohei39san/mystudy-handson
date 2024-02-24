output "instance_public_key" {
  description = "instance public key"
  value       = var.instance_public_key
}

output "instance_private_key" {
  description = "instance private key"
  value       = var.instance_private_key
}

output "instance" {
  description = "ec2"
  value       = aws_instance.instance
}
