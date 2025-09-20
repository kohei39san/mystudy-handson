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

variable "allowed_cidr" {
  description = "CIDR block allowed to access the load balancer"
  type        = string
  default     = "0.0.0.0/0"
}

# MySQL Variables
variable "mysql_admin_password" {
  description = "MySQL admin password"
  type        = string
  sensitive   = true
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
  default     = "admin@example.com"
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