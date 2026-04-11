# ─────────────────────────────────────────────────────────────────────────────
# Outputs: 結合テストで使用するリソース ID
# ─────────────────────────────────────────────────────────────────────────────

# --- AWS ---

output "aws_ec2_instance_id" {
  description = "EC2 インスタンス ID（--resource-id に指定）"
  value       = aws_instance.test.id
}

output "aws_ec2_public_ip" {
  description = "EC2 パブリック IP アドレス"
  value       = aws_instance.test.public_ip
}

output "aws_ec2_private_ip" {
  description = "EC2 プライベート IP アドレス"
  value       = aws_instance.test.private_ip
}

output "aws_rds_identifier" {
  description = "RDS DB インスタンス識別子（--resource-id に指定）"
  value       = aws_db_instance.test.identifier
}

output "aws_rds_endpoint" {
  description = "RDS エンドポイント（ホスト:ポート）"
  value       = aws_db_instance.test.endpoint
}

output "aws_vpc_id" {
  description = "AWS VPC ID"
  value       = aws_vpc.main.id
}

# --- Azure ---

output "azure_vm_resource_id" {
  description = "Azure VM リソース ID（--resource-id に指定）"
  value       = azurerm_linux_virtual_machine.test.id
}

output "azure_vm_public_ip" {
  description = "Azure VM パブリック IP アドレス"
  value       = azurerm_public_ip.vm.ip_address
}

output "azure_vm_private_ip" {
  description = "Azure VM プライベート IP アドレス"
  value       = azurerm_network_interface.vm.private_ip_address
}

# --- GCP ---

output "gcp_vm_resource_id" {
  description = "GCP VM リソース ID（--resource-id に指定: projects/<project>/zones/<zone>/instances/<name> 形式）"
  value       = "projects/${var.gcp_project_id}/zones/${var.gcp_zone}/instances/${google_compute_instance.test.name}"
}

output "gcp_vm_external_ip" {
  description = "GCP VM 外部 IP アドレス"
  value       = google_compute_instance.test.network_interface[0].access_config[0].nat_ip
}

output "gcp_vm_internal_ip" {
  description = "GCP VM 内部 IP アドレス"
  value       = google_compute_instance.test.network_interface[0].network_ip
}

output "gcp_cloudrun_resource_id" {
  description = "GCP Cloud Run リソース ID（--resource-id に指定: projects/<project>/locations/<region>/services/<name> 形式）"
  value       = "projects/${var.gcp_project_id}/locations/${var.gcp_region}/services/${google_cloud_run_v2_service.test.name}"
}

output "gcp_cloudrun_uri" {
  description = "GCP Cloud Run サービス URI"
  value       = google_cloud_run_v2_service.test.uri
}
