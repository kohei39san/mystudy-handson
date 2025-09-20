# tflint-ignore-file: terraform_typed_variables
variable "compartment_ocid" {}
variable "region" {}

variable "bucket_name" {
  description = "The name of the bucket for storing Terraform state"
  type        = string
  default     = "terraform_state_bucket"
}