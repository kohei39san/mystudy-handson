# MySQL HeatWave Database System
resource "oci_mysql_mysql_db_system" "redmine_mysql" {
  compartment_id = var.compartment_id

  admin_password      = var.mysql_admin_password
  admin_username      = "admin"
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  shape_name          = "MySQL.Free"

  subnet_id = oci_core_subnet.mysql_subnet.id

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
resource "null_resource" "create_redmine_database" {
  depends_on = [oci_mysql_mysql_db_system.redmine_mysql]

  provisioner "local-exec" {
    command = <<-EOT
      # Wait for MySQL to be available
      sleep 60
      
      # Create database and user for Redmine
      # Note: This is a placeholder - in production, you would use proper MySQL client tools
      echo "Database creation would be handled through MySQL client or application initialization"
    EOT
  }

  triggers = {
    mysql_id = oci_mysql_mysql_db_system.redmine_mysql.id
  }
}