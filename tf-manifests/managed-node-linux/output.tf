output "ssh_cmd" {
  description = "ssh cmd"
  value       = "ssh -i ${module.common_resources.private_key} ec2-user@${module.common_resources.instance.id} -o ProxyCommand='aws ec2-instance-connect open-tunnel --instance-id ${module.common_resources.instance.id}'"
}
