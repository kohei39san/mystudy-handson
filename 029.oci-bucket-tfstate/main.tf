terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 7.0"
    }
  }
}

provider "oci" {}

resource "oci_objectstorage_bucket" "tfstate_bucket" {
  compartment_id = var.compartment_id
  name           = var.bucket_name
  namespace      = data.oci_objectstorage_namespace.ns.namespace

  versioning = "Enabled"

  public_access_type = "NoPublicAccess"

  storage_tier = "Standard"

  object_events_enabled = false

  freeform_tags = {
    Purpose = "terraform-state"
  }
}

data "oci_objectstorage_namespace" "ns" {
  compartment_id = var.compartment_id
}