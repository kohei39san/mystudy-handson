# Outputs for OCI Redmine Deployment

output "load_balancer_ip" {
  description = "Public IP address of the Network Load Balancer"
  value       = oci_network_load_balancer_network_load_balancer.redmine_nlb.ip_addresses[0].ip_address
}

output "redmine_url" {
  description = "URL to access Redmine application"
  value       = "http://${oci_network_load_balancer_network_load_balancer.redmine_nlb.ip_addresses[0].ip_address}"
}

output "mysql_endpoint" {
  description = "MySQL HeatWave hostname"
  value       = oci_mysql_mysql_db_system.redmine_mysql.hostname_label
  sensitive   = true
}

output "mysql_ip_address" {
  description = "MySQL HeatWave IP address"
  value       = oci_mysql_mysql_db_system.redmine_mysql.ip_address
  sensitive   = true
}

output "container_instance_id" {
  description = "Container Instance OCID"
  value       = oci_container_instances_container_instance.redmine_container.id
}

output "container_instance_private_ip" {
  description = "Container Instance private IP address"
  value       = oci_container_instances_container_instance.redmine_container.vnics[0].private_ip
}

output "vcn_id" {
  description = "VCN OCID"
  value       = oci_core_vcn.redmine_vcn.id
}

output "public_subnet_id" {
  description = "Public subnet OCID"
  value       = oci_core_subnet.public_subnet.id
}

output "private_subnet_id" {
  description = "Private subnet OCID"
  value       = oci_core_subnet.private_subnet.id
}

output "mysql_subnet_id" {
  description = "MySQL subnet OCID"
  value       = oci_core_subnet.mysql_subnet.id
}