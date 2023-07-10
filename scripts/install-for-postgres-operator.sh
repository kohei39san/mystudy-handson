#!/bin/bash -ex

echo "install terraform"
sudo yum install -y yum-utils shadow-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install terraform

echo "setup minikube"
eval $(minikube docker-env)
echo 'eval $(minikube docker-env)' >> ~/.bash_profile

echo "deploy postgres operator"
echo "user=zalando" >> /tmp/k8s-manifests/.pgpass
echo "password=$(openssl rand -base64 12 | fold -w 12 | head -1)" >> /tmp/k8s-manifests/.pgpass
cd /tmp/k8s-manifests
terraform init
terraform apply -auto-approve
