variable "compartment_ocid" {
  description = "The OCID of the compartment"
  type        = string
}

variable "region" {
  description = "The OCI region"
  type        = string
}

variable "bucket_name" {
  description = "The name of the bucket for storing Terraform state"
  type        = string
  default     = "terraform_state_bucket"
}