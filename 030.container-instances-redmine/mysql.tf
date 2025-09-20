# MySQL HeatWave Database System
resource "oci_mysql_mysql_db_system" "redmine_mysql" {
  compartment_id = var.compartment_id

  admin_password      = var.mysql_admin_password
  admin_username      = var.mysql_admin_username
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  shape_name          = "MySQL.Free"

  subnet_id = oci_core_subnet.mysql_subnet.id
  nsg_ids   = [oci_core_network_security_group.mysql_nsg.id]
  mysql_version = var.mysql_version

  display_name = "redmine-mysql"
  description  = "MySQL HeatWave for Redmine application"

  data_storage_size_in_gb = 50
  hostname_label          = "redmine-mysql"

  backup_policy {
    is_enabled        = true
    retention_in_days = 7
    window_start_time = "02:00-00:00"
  }

  maintenance {
    window_start_time = "SUNDAY 02:00"
  }

  freeform_tags = var.freeform_tags
}

# Note: MySQL.Free shape uses default configuration, custom configurations are not supported

# Create database for Redmine
resource "oci_functions_invoke_function" "create_redmine_database" {
  function_id = oci_functions_function.mysql_init_function.id
  
  invoke_function_body = "{}"
  
  depends_on = [oci_functions_function.mysql_init_function, oci_mysql_mysql_db_system.redmine_mysql]
}