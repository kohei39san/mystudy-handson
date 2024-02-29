#!/bin/bash -ex

TF_DIR=$1
cd "${TF_DIR}"
terraform init
terraform apply -auto-approve
