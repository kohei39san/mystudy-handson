variable "auth_token_user_id" {
  type        = string
  description = "The OCID of the user for which the auth token will be created"
}

resource "oci_identity_auth_token" "auth_token" {
  description = "Auth token for Container Repository"
  user_id     = var.auth_token_user_id
}