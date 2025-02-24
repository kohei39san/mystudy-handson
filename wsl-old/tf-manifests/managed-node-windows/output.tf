output "rdp_cmd_for_wsl" {
  description = "rdp cmd for wsl"
  value       = <<EOT
aws ec2 get-password-data --instance-id ${module.common.instance.id} --priv-launch-key ${var.key_pair_private}
/mnt/c/Windows/System32/mstsc.exe /v:${module.common.instance.public_ip}:${var.rdp_port}
EOT
}
