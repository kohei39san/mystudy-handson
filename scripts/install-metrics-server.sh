#!/bin/bash -ex

VERSION="v0.6.3"
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/${VERSION}/components.yaml
kubectl patch deploy -n kube-system metrics-server --type=json -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/5", "value": "--kubelet-insecure-tls" }]'
