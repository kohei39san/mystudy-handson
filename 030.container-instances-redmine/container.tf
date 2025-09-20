# Container Instance for Redmine
resource "oci_container_instances_container_instance" "redmine_container" {
  compartment_id      = var.compartment_id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  
  display_name = "redmine-container-instance"
  
  shape = "CI.Standard.A1.Flex"
  shape_config {
    ocpus         = 1
    memory_in_gbs = 4
  }
  
  vnics {
    subnet_id              = oci_core_subnet.private_subnet.id
    assign_public_ip       = false
    display_name           = "redmine-vnic"
    hostname_label         = "redmine"
    skip_source_dest_check = false
  }
  
  containers {
    display_name = "redmine"
    image_url    = "docker.io/bitnami/redmine:6.0.6"
    
    environment_variables = {
      "REDMINE_DATABASE_TYPE"     = "mysql2"
      "REDMINE_DATABASE_HOST"     = oci_mysql_mysql_db_system.redmine_mysql.ip_address
      "REDMINE_DATABASE_PORT"     = "3306"
      "REDMINE_DATABASE_NAME"     = "redmine"
      "REDMINE_DATABASE_USER"     = "redmine"
      "REDMINE_DATABASE_PASSWORD" = var.redmine_db_password
      "REDMINE_USERNAME"          = var.redmine_admin_username
      "REDMINE_PASSWORD"          = var.redmine_admin_password
      "REDMINE_EMAIL"             = var.redmine_admin_email
      "REDMINE_LANGUAGE"          = "ja"
    }
    
    resource_config {
      memory_limit_in_gbs = 3.5
      vcpus_limit         = 1
    }
    
    health_checks {
      health_check_type = "HTTP"
      path              = "/"
      port              = 3000
      interval_in_seconds = 30
      timeout_in_seconds  = 10
      failure_threshold   = 3
      success_threshold   = 1
    }
    
    volume_mounts {
      mount_path  = "/bitnami/redmine"
      volume_name = "redmine-data"
    }
  }
  
  volumes {
    name        = "redmine-data"
    volume_type = "EMPTYDIR"
    backing_store = "EPHEMERAL_STORAGE"
  }
  
  container_restart_policy = "ALWAYS"
  
  freeform_tags = {
    "Environment" = "production"
    "Application" = "redmine"
  }
  
  depends_on = [oci_mysql_mysql_db_system.redmine_mysql]
}

# Wait for container to be ready
resource "time_sleep" "wait_for_container" {
  depends_on = [oci_container_instances_container_instance.redmine_container]
  create_duration = "120s"
}