# VCN
resource "oci_core_vcn" "redmine_vcn" {
  compartment_id = var.compartment_id
  cidr_blocks    = [var.vcn_cidr]
  display_name   = "redmine-vcn"
  dns_label      = "redminevcn"
}

# Internet Gateway
resource "oci_core_internet_gateway" "redmine_igw" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-igw"
}

# Public Subnet for Load Balancer
resource "oci_core_subnet" "public_subnet" {
  compartment_id      = var.compartment_id
  vcn_id              = oci_core_vcn.redmine_vcn.id
  cidr_block          = var.public_subnet_cidr
  display_name        = "redmine-public-subnet"
  dns_label           = "publicsubnet"
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  route_table_id      = oci_core_route_table.public_rt.id
}

# Private Subnet for Container Instance
resource "oci_core_subnet" "private_subnet" {
  compartment_id                 = var.compartment_id
  vcn_id                         = oci_core_vcn.redmine_vcn.id
  cidr_block                     = var.private_subnet_cidr
  display_name                   = "redmine-private-subnet"
  dns_label                      = "privatesubnet"
  availability_domain            = data.oci_identity_availability_domains.ads.availability_domains[0].name
  route_table_id                 = oci_core_route_table.private_rt.id
  prohibit_public_ip_on_vnic     = true
  prohibit_internet_ingress      = true
}

# Private Subnet for MySQL
resource "oci_core_subnet" "mysql_subnet" {
  compartment_id                 = var.compartment_id
  vcn_id                         = oci_core_vcn.redmine_vcn.id
  cidr_block                     = var.mysql_subnet_cidr
  display_name                   = "redmine-mysql-subnet"
  dns_label                      = "mysqlsubnet"
  availability_domain            = data.oci_identity_availability_domains.ads.availability_domains[0].name
  route_table_id                 = oci_core_route_table.private_rt.id
  prohibit_public_ip_on_vnic     = true
  prohibit_internet_ingress      = true
}

# NAT Gateway
resource "oci_core_nat_gateway" "redmine_nat" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-nat"
}

# Route Tables
resource "oci_core_route_table" "public_rt" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.redmine_igw.id
  }
}

resource "oci_core_route_table" "private_rt" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-private-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_nat_gateway.redmine_nat.id
  }
}

# Network Security Groups
# Load Balancer NSG
resource "oci_core_network_security_group" "lb_nsg" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-lb-nsg"
  freeform_tags  = var.freeform_tags
}

# Container NSG
resource "oci_core_network_security_group" "container_nsg" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-container-nsg"
  freeform_tags  = var.freeform_tags
}

# Function NSG
resource "oci_core_network_security_group" "function_nsg" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-function-nsg"
  freeform_tags  = var.freeform_tags
}

# MySQL NSG
resource "oci_core_network_security_group" "mysql_nsg" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-mysql-nsg"
  freeform_tags  = var.freeform_tags
}

# NSG Rules
# Load Balancer NSG Rules
resource "oci_core_network_security_group_security_rule" "lb_ingress_http" {
  network_security_group_id = oci_core_network_security_group.lb_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = var.allowed_cidr
  source_type               = "CIDR_BLOCK"
  
  tcp_options {
    destination_port_range {
      min = var.http_port
      max = var.http_port
    }
  }
}

resource "oci_core_network_security_group_security_rule" "lb_ingress_https" {
  network_security_group_id = oci_core_network_security_group.lb_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = var.allowed_cidr
  source_type               = "CIDR_BLOCK"
  
  tcp_options {
    destination_port_range {
      min = var.https_port
      max = var.https_port
    }
  }
}

resource "oci_core_network_security_group_security_rule" "lb_egress_container" {
  network_security_group_id = oci_core_network_security_group.lb_nsg.id
  direction                 = "EGRESS"
  protocol                  = "6"
  destination               = oci_core_network_security_group.container_nsg.id
  destination_type          = "NETWORK_SECURITY_GROUP"
  
  tcp_options {
    destination_port_range {
      min = var.redmine_port
      max = var.redmine_port
    }
  }
}

# Container NSG Rules
resource "oci_core_network_security_group_security_rule" "container_ingress_lb" {
  network_security_group_id = oci_core_network_security_group.container_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = oci_core_network_security_group.lb_nsg.id
  source_type               = "NETWORK_SECURITY_GROUP"
  
  tcp_options {
    destination_port_range {
      min = var.redmine_port
      max = var.redmine_port
    }
  }
}

resource "oci_core_network_security_group_security_rule" "container_egress_mysql" {
  network_security_group_id = oci_core_network_security_group.container_nsg.id
  direction                 = "EGRESS"
  protocol                  = "6"
  destination               = oci_core_network_security_group.mysql_nsg.id
  destination_type          = "NETWORK_SECURITY_GROUP"
  
  tcp_options {
    destination_port_range {
      min = var.mysql_port
      max = var.mysql_port
    }
  }
}

resource "oci_core_network_security_group_security_rule" "container_egress_all" {
  network_security_group_id = oci_core_network_security_group.container_nsg.id
  direction                 = "EGRESS"
  protocol                  = "all"
  destination               = "0.0.0.0/0"
  destination_type          = "CIDR_BLOCK"
}

# Function NSG Rules
resource "oci_core_network_security_group_security_rule" "function_egress_mysql" {
  network_security_group_id = oci_core_network_security_group.function_nsg.id
  direction                 = "EGRESS"
  protocol                  = "6"
  destination               = oci_core_network_security_group.mysql_nsg.id
  destination_type          = "NETWORK_SECURITY_GROUP"
  
  tcp_options {
    destination_port_range {
      min = var.mysql_port
      max = var.mysql_port
    }
  }
}

resource "oci_core_network_security_group_security_rule" "function_egress_all" {
  network_security_group_id = oci_core_network_security_group.function_nsg.id
  direction                 = "EGRESS"
  protocol                  = "all"
  destination               = "0.0.0.0/0"
  destination_type          = "CIDR_BLOCK"
}

# MySQL NSG Rules
resource "oci_core_network_security_group_security_rule" "mysql_ingress_container" {
  network_security_group_id = oci_core_network_security_group.mysql_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = oci_core_network_security_group.container_nsg.id
  source_type               = "NETWORK_SECURITY_GROUP"
  
  tcp_options {
    destination_port_range {
      min = var.mysql_port
      max = var.mysql_port
    }
  }
}

resource "oci_core_network_security_group_security_rule" "mysql_ingress_function" {
  network_security_group_id = oci_core_network_security_group.mysql_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = oci_core_network_security_group.function_nsg.id
  source_type               = "NETWORK_SECURITY_GROUP"
  
  tcp_options {
    destination_port_range {
      min = var.mysql_port
      max = var.mysql_port
    }
  }
}

resource "oci_core_network_security_group_security_rule" "mysql_ingress_x_protocol" {
  network_security_group_id = oci_core_network_security_group.mysql_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = oci_core_network_security_group.container_nsg.id
  source_type               = "NETWORK_SECURITY_GROUP"
  
  tcp_options {
    destination_port_range {
      min = var.mysql_x_protocol_port
      max = var.mysql_x_protocol_port
    }
  }
}