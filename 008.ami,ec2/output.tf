output "ssh_cmd" {
  description = "ssh cmd"
  value       = "ssh -i '${var.key_pair_private}' ec2-user@${aws_instance.instance.public_ip}"
}
