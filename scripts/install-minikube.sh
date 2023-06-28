#!/bin/bash -ex

echo 'install minikube'
KUBE_VERSION="v1.25.3"
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube start \
--kubernetes-version=${KUBE_VERSION} \
--driver=docker

echo 'install kubectl'
WD=/tmp/kubectl
mkdir -p ${WD}
cd ${WD}
curl -LO https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

echo "setup addon"
minikube addons enable metrics-server

echo 'setup alias'
#echo 'alias k="minikube kubectl --"' >> ~/.bash_profile
#echo 'alias kubectl="minikube kubectl --"' >> ~/.bash_profile
echo 'alias k="kubectl"' >> ~/.bash_profile
echo 'complete -F __start_kubectl k' >> ~/.bash_profile
echo 'source <(kubectl completion bash)' >> ~/.bash_profile
