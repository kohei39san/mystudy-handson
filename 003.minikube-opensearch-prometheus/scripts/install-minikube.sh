#!/bin/bash

echo "install minikube"

cd /tmp
curl -LO https://github.com/kubernetes/minikube/releases/download/v1.34.0/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
minikube start --kubernetes-version v1.31.2 --cpus no-limit --memory no-limit

echo "kubectl complete"

echo "source <(minikube kubectl -- completion bash)" >> ~/.bashrc
echo "alias kubectl='minikube kubectl --'" >> ~/.bashrc
echo "alias k=kubectl" >> ~/.bashrc
echo "complete -F __start_kubectl k" >> ~/.bashrc

echo "setup node"
sudo sysctl -w vm.max_map_count=262144