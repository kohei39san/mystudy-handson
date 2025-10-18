# OCI Container Repository
resource "oci_artifacts_container_repository" "mysql_init_repo" {
  compartment_id = var.compartment_id
  display_name   = "mysql-init"
  is_public      = false

  freeform_tags = var.freeform_tags
}