# Variables for OCI Redmine Deployment

variable "region" {
  description = "OCI region"
  type        = string
  default     = "ap-osaka-1"
}

variable "compartment_id" {
  description = "OCI compartment OCID"
  type        = string
}

variable "tenancy_ocid" {
  description = "OCI tenancy OCID"
  type        = string
}

variable "allowed_cidr" {
  description = "CIDR block allowed to access the load balancer"
  type        = string
  default     = "127.0.0.1/32"
}

# Network Variables
variable "vcn_cidr" {
  description = "VCN CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Public subnet CIDR block"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "Private subnet CIDR block"
  type        = string
  default     = "10.0.2.0/24"
}

variable "mysql_subnet_cidr" {
  description = "MySQL subnet CIDR block"
  type        = string
  default     = "10.0.3.0/24"
}

# Port Variables
variable "http_port" {
  description = "HTTP port"
  type        = number
  default     = 80
}

variable "https_port" {
  description = "HTTPS port"
  type        = number
  default     = 443
}

variable "redmine_port" {
  description = "Redmine application port"
  type        = number
  default     = 3000
}

variable "mysql_x_protocol_port" {
  description = "MySQL X Protocol port"
  type        = number
  default     = 33060
}

# MySQL Variables
variable "mysql_admin_username" {
  description = "MySQL admin username"
  type        = string
  default     = "admin"
}

variable "mysql_admin_password" {
  description = "MySQL admin password"
  type        = string
  sensitive   = true
}

variable "mysql_port" {
  description = "MySQL port"
  type        = number
  default     = 3306
}

variable "mysql_version" {
  description = "MySQL version"
  type        = string
  default     = "8.0.35"
}

# Redmine Database Variables
variable "redmine_database_type" {
  description = "Redmine database type"
  type        = string
  default     = "mysql2"
}

# Redmine Variables
variable "redmine_db_password" {
  description = "Redmine database password"
  type        = string
  sensitive   = true
}

variable "redmine_admin_username" {
  description = "Redmine admin username"
  type        = string
  default     = "admin"
}

variable "redmine_admin_password" {
  description = "Redmine admin password"
  type        = string
  sensitive   = true
}

variable "redmine_admin_email" {
  description = "Redmine admin email"
  type        = string
  default     = "admin@invalid.com"
}

# Tags
variable "freeform_tags" {
  description = "Freeform tags to apply to resources"
  type        = map(string)
  default = {
    "Environment" = "production"
    "Application" = "redmine"
    "ManagedBy"   = "terraform"
  }
}