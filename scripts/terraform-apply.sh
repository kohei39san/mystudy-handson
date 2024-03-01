#!/bin/bash -ex

if [[ -z ${TF_DIR} ]]; then
  TF_DIR=""
fi
cd "${TF_DIR}"
terraform init
terraform apply -auto-approve
