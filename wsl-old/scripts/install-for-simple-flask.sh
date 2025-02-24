#!/bin/bash -ex

echo "install git"
sudo yum install -y git
cd /tmp
git clone https://github.com/kohei39san/mystudy-handson.git
cd mystudy-handson
git checkout feature/simple-flask
git submodule update --init

echo "install terraform"
sudo yum install -y yum-utils shadow-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install terraform

#echo "setup minikube"
#eval $(minikube docker-env)
#echo 'eval $(minikube docker-env)' >> ~/.bash_profile
#minikube addons enable registry

#echo "setup nginx"
#sudo amazon-linux-extras install nginx1 -y
#sudo systemctl start nginx.service

#echo "build nginx ingress controller"
#cd /tmp/mystudy-handson/container-images/kubernetes-ingress
#make debian-image TARGET=container
#minikube image load nginx/nginx-ingress:$(docker images | grep nginx-ingress | awk '{print $2}')

echo "deploy k8s objects"
echo "user=zalando" >> /tmp/mystudy-handson/k8s-manifests/simple-flask/.pgpass
echo "password=$(openssl rand -base64 12 | fold -w 12 | head -1)" >> /tmp/mystudy-handson/k8s-manifests/simple-flask/.pgpass
cd /tmp/mystudy-handson/k8s-manifests/simple-flask
terraform init
terraform apply -auto-approve
