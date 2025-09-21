#!/bin/bash
# OCI backend config variables for Terraform

config_file_profile="DEFAULT"
bucket="terraform_state_bucket"
auth_cli="security_token"
auth="SecurityToken"

# OCI Object Storage namespaceの取得
namespace="$(oci os ns get --query data --raw-output --auth "$auth_cli")"

# 現在のディレクトリ名を取得し、tfstateファイル名を生成
key="$(basename "$(pwd)")-terraform.tfstate"

# OCIのregion名を取得
region="$(oci iam region-subscription list --auth "$auth_cli" --query 'data[0]."region-name"' --raw-output)"