#!/bin/bash -ex

curl -sSLf https://get.k0s.sh | sudo K0S_VERSION=v1.27.2+k0s.0 sh
sudo /usr/local/bin/k0s install controller --single
sudo /usr/local/bin/k0s start
echo "waiting k0s start ..."
sleep 30
sudo /usr/local/bin/k0s status
sudo /usr/local/bin/k0s kubectl get node
