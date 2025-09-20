# OCI Functions Application
resource "oci_functions_application" "mysql_init_app" {
  compartment_id = var.compartment_id
  display_name   = "mysql-init-app"
  subnet_ids     = [oci_core_subnet.private_subnet.id]
  network_security_group_ids = [oci_core_network_security_group.function_nsg.id]

  freeform_tags = var.freeform_tags
}

# OCI Functions Function for MySQL initialization
resource "oci_functions_function" "mysql_init_function" {
  depends_on = [docker_registry_image.mysql_init_registry_image]
  
  application_id = oci_functions_application.mysql_init_app.id
  display_name   = "mysql-init-function"
  image          = docker_registry_image.mysql_init_registry_image.name
  memory_in_mbs  = 128
  timeout_in_seconds = 30

  config = {
    MYSQL_HOST     = oci_mysql_mysql_db_system.redmine_mysql.ip_address
    MYSQL_PORT     = var.mysql_port
    MYSQL_ADMIN_USER = var.mysql_admin_username
    MYSQL_ADMIN_PASSWORD = var.mysql_admin_password
    REDMINE_DB_PASSWORD = var.redmine_db_password
  }

  freeform_tags = var.freeform_tags
}