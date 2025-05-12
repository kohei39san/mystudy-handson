locals {
  is_bitnami = true  # Set to true since we're using Bitnami Redmine AMI
  private_key_path = var.private_key_path  # Path to the private key for SSH
}