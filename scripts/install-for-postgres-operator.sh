#!/bin/bash -ex

echo "install terraform"
sudo yum install -y yum-utils shadow-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install terraform

echo "deploy postgres operator"
cd /tmp/k8s-manifests
terraform init
terraform apply -auto-approve
