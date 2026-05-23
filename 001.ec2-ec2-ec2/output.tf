output "ssh_cmd" {
  description = "to access ec2 by ssh"
  value       = "ssh -i '${var.instance_private_key}' ec2-user@${aws_instance.test_instance.public_ip}"
}

output "ssh_cmd_to_private" {
  description = "to access ec2 private by ssh"
  value       = "ssh -o ProxyCommand='ssh -i \"${var.instance_private_key}\" -W %h:%p ec2-user@${aws_instance.test_instance.public_ip}' -i '${var.instance_private_key}' ec2-user@${aws_instance.private_server.private_ip}"
}