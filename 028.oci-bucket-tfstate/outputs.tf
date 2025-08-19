output "bucket_name" {
  description = "The name of the created bucket"
  value       = oci_objectstorage_bucket.tfstate_bucket.name
}

output "bucket_namespace" {
  description = "The namespace of the bucket"
  value       = data.oci_objectstorage_namespace.ns.namespace
}

output "bucket_url" {
  description = "The URL of the bucket"
  value       = "https://objectstorage.${var.region}.oraclecloud.com/n/${data.oci_objectstorage_namespace.ns.namespace}/b/${oci_objectstorage_bucket.tfstate_bucket.name}"
}