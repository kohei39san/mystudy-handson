$config_file_profile = "DEFAULT"
$bucket = "terraform_state_bucket"
$auth_cli="security_token"
$auth = "SecurityToken"
$namespace = (oci os ns get --query data --raw-output --auth $auth_cli)
$key = "$(Split-Path -Leaf (Get-Location))-terraform.tfstate"
$region = (oci iam region-subscription list --auth $auth_cli --query 'data[0].\"region-name\"' --raw-output)