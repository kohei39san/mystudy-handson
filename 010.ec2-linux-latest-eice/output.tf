output "ssh_cmd" {
  description = "ssh cmd"
  value       = "ssh -i '${var.key_pair_private}' ec2-user@${aws_instance.instance.id} -o ProxyCommand='aws ec2-instance-connect open-tunnel --instance-id ${aws_instance.instance.id}'"
}
