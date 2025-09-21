#!/bin/bash
# Usage: ./terraform-init-oci-be.sh [terraform init args]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# OCIバックエンド設定の読み込み
source "$SCRIPT_DIR/terraform-conf-oci-be.sh"

terraform init "$@" \
    -backend-config="namespace=$namespace" \
    -backend-config="bucket=$bucket" \
    -backend-config="config_file_profile=$config_file_profile" \
    -backend-config="auth=$auth" \
    -backend-config="key=$key" \
    -backend-config="region=$region"