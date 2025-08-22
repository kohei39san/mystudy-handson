$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. "$scriptDir\terraform-conf-oci-be.ps1"

terraform init @args -backend-config="namespace=$namespace" `
    -backend-config="bucket=$bucket" `
    -backend-config="config_file_profile=$config_file_profile" `
    -backend-config="auth=$auth" `
    -backend-config="key=$key" `
    -backend-config="region=$region"