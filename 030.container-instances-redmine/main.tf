# OCI Provider Configuration
terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "oci" {
  region = var.region
}

# Data sources
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

# VCN
resource "oci_core_vcn" "redmine_vcn" {
  compartment_id = var.compartment_id
  cidr_blocks    = ["10.0.0.0/16"]
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
  cidr_block          = "10.0.1.0/24"
  display_name        = "redmine-public-subnet"
  dns_label           = "publicsubnet"
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  route_table_id      = oci_core_route_table.public_rt.id
  security_list_ids   = [oci_core_security_list.public_sl.id]
}

# Private Subnet for Container Instance
resource "oci_core_subnet" "private_subnet" {
  compartment_id                 = var.compartment_id
  vcn_id                         = oci_core_vcn.redmine_vcn.id
  cidr_block                     = "10.0.2.0/24"
  display_name                   = "redmine-private-subnet"
  dns_label                      = "privatesubnet"
  availability_domain            = data.oci_identity_availability_domains.ads.availability_domains[0].name
  route_table_id                 = oci_core_route_table.private_rt.id
  security_list_ids              = [oci_core_security_list.private_sl.id]
  prohibit_public_ip_on_vnic     = true
  prohibit_internet_ingress      = true
}

# Private Subnet for MySQL
resource "oci_core_subnet" "mysql_subnet" {
  compartment_id                 = var.compartment_id
  vcn_id                         = oci_core_vcn.redmine_vcn.id
  cidr_block                     = "10.0.3.0/24"
  display_name                   = "redmine-mysql-subnet"
  dns_label                      = "mysqlsubnet"
  availability_domain            = data.oci_identity_availability_domains.ads.availability_domains[0].name
  route_table_id                 = oci_core_route_table.private_rt.id
  security_list_ids              = [oci_core_security_list.mysql_sl.id]
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

# Security Lists
resource "oci_core_security_list" "public_sl" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-public-sl"

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  ingress_security_rules {
    protocol = "6"
    source   = var.allowed_cidr

    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = var.allowed_cidr

    tcp_options {
      min = 443
      max = 443
    }
  }
}

resource "oci_core_security_list" "private_sl" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-private-sl"

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  ingress_security_rules {
    protocol = "6"
    source   = "10.0.1.0/24"

    tcp_options {
      min = 3000
      max = 3000
    }
  }
}

resource "oci_core_security_list" "mysql_sl" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.redmine_vcn.id
  display_name   = "redmine-mysql-sl"

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  ingress_security_rules {
    protocol = "6"
    source   = "10.0.2.0/24"

    tcp_options {
      min = 3306
      max = 3306
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "10.0.2.0/24"

    tcp_options {
      min = 33060
      max = 33060
    }
  }
}