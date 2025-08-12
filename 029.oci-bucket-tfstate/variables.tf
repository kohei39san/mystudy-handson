variable "compartment_id" {
  description = "The OCID of the compartment"
  type        = string
}

variable "bucket_name" {
  description = "The name of the bucket for storing Terraform state"
  type        = string
  default     = "terraform-state-bucket"
}