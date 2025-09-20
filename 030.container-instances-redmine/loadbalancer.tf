# Network Load Balancer
resource "oci_network_load_balancer_network_load_balancer" "redmine_nlb" {
  compartment_id = var.compartment_id
  display_name   = "redmine-nlb"

  subnet_id                  = oci_core_subnet.public_subnet.id
  network_security_group_ids = [oci_core_network_security_group.lb_nsg.id]

  is_private                     = false
  is_preserve_source_destination = false

  freeform_tags = var.freeform_tags
}

# Backend Set
resource "oci_network_load_balancer_backend_set" "redmine_backend_set" {
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.redmine_nlb.id
  name                     = "redmine-backend-set"
  policy                   = "FIVE_TUPLE_HASH"

  health_checker {
    protocol           = "HTTP"
    port               = 3000
    url_path           = "/"
    return_code        = 200
    timeout_in_millis  = 10000
    interval_in_millis = 30000
    retries            = 3
  }

  is_preserve_source = false
}

# Backend (Container Instance)
resource "oci_network_load_balancer_backend" "redmine_backend" {
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.redmine_nlb.id
  backend_set_name         = oci_network_load_balancer_backend_set.redmine_backend_set.name

  ip_address = oci_container_instances_container_instance.redmine_container.vnics[0].private_ip
  port       = 3000
  weight     = 1

  depends_on = [oci_container_instances_container_instance.redmine_container]
}

# Listener for HTTP
resource "oci_network_load_balancer_listener" "redmine_listener_http" {
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.redmine_nlb.id
  name                     = "redmine-listener-http"
  default_backend_set_name = oci_network_load_balancer_backend_set.redmine_backend_set.name
  port                     = 80
  protocol                 = "TCP"
}

# Listener for HTTPS (optional, for future SSL termination)
resource "oci_network_load_balancer_listener" "redmine_listener_https" {
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.redmine_nlb.id
  name                     = "redmine-listener-https"
  default_backend_set_name = oci_network_load_balancer_backend_set.redmine_backend_set.name
  port                     = 443
  protocol                 = "TCP"
}

