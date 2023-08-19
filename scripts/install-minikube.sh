#!/bin/bash -ex

echo 'install minikube'
if [[ -z ${KUBE_VERSION} ]];then
  KUBE_VERSION="v1.25.3"
fi
cd /tmp
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube start \
--kubernetes-version=${KUBE_VERSION} \
--driver=docker

echo 'install helm'
if [[ -z ${HELM_VERSION} ]];then
  HELM_VERSION='v3.10.3'
fi
WD=/tmp/helm
mkdir -p ${WD}
cd ${WD}
curl "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" -o helm.tar.gz
tar -zxvf helm.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
helm version

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
