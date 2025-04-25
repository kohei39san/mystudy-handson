data "http" "client_global_ip" {
  url = "https://inet-ip.info"
  version = "1.2.0" # Assuming this is the correct version
}
locals {
  allowed_cidr = replace("${data.http.client_global_ip.response_body}/32", "\n", "")
}
