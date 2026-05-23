output "rdp_cmd_for_wsl" {
  description = "rdp cmd for wsl"
  value       = <<EOT
aws ec2 get-password-data --instance-id ${aws_instance.instance.id} --priv-launch-key '${var.key_pair_private}'
mstsc.exe /v:${aws_instance.instance.public_ip}:${var.rdp_port}
EOT
}

output "rdp_user" {
  description = "rdp user"
  value       = "Administrator"
}