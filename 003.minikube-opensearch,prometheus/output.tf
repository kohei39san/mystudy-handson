output "ssh_cmd" {
  description = "ssh cmd"
  value       = "ssh -i '${var.instance_private_key}' ec2-user@${aws_instance.instance.public_ip}"
}
