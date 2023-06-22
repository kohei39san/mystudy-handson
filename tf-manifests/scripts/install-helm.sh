#!/bin/bash -ex

echo 'install helm'
HELM_VERSION='v3.10.3'
WD=/tmp/helm
mkdir -p ${WD}
cd ${WD}
curl "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" -o helm.tar.gz
tar -zxvf helm.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
helm version
