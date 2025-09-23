# MySQL HeatWave Database System
resource "oci_mysql_mysql_db_system" "redmine_mysql" {
  compartment_id = var.compartment_id
  shape_name          = "MySQL.Free"
  subnet_id     = oci_core_subnet.mysql_subnet.id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  admin_password      = var.mysql_admin_password
  admin_username      = var.mysql_admin_username
  display_name = "RedmineMySQL"
  description  = "MySQL HeatWave for Redmine application"
  deletion_policy {
    automatic_backup_retention = "DELETE"
  }
  nsg_ids       = [oci_core_network_security_group.mysql_nsg.id]
  freeform_tags = var.freeform_tags
}

# Note: MySQL.Free shape uses default configuration, custom configurations are not supported

# Create database for Redmine
resource "oci_functions_invoke_function" "create_redmine_database" {
  function_id = oci_functions_function.mysql_init_function.id

  invoke_function_body = "{}"

  depends_on = [oci_functions_function.mysql_init_function, oci_mysql_mysql_db_system.redmine_mysql]
}