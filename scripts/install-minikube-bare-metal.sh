#!/bin/bash -ex

echo "install cni plugin"
if [[ -z ${CNI_PLUGIN_VERSION} ]];then
  CNI_PLUGIN_VERSION="v1.4.0"
fi
cd /tmp
CNI_PLUGIN_TAR="cni-plugins-linux-amd64-$CNI_PLUGIN_VERSION.tgz"
CNI_PLUGIN_INSTALL_DIR="/opt/cni/bin"
curl -LO "https://github.com/containernetworking/plugins/releases/download/$CNI_PLUGIN_VERSION/$CNI_PLUGIN_TAR"
sudo mkdir -p "$CNI_PLUGIN_INSTALL_DIR"
sudo tar -xf "$CNI_PLUGIN_TAR" -C "$CNI_PLUGIN_INSTALL_DIR"
rm "$CNI_PLUGIN_TAR"

echo "install cri"
if [[ -z ${CRI_VERSION} ]];then
  CRI_VERSION="v0.3.10"
fi
git clone https://github.com/Mirantis/cri-dockerd.git
cd cri-dockerd
git checkout "${CRI_VERSION}"
sudo chown -R root:root .
docker run --rm -v /tmp/cri-dockerd:/tmp/cri-dockerd -w /tmp/cri-dockerd -e "ARCH=amd64" --name golang golang:1.20.12 make cri-dockerd
sudo install -o root -g root -m 0755 cri-dockerd /usr/local/bin/cri-dockerd
sudo install packaging/systemd/* /etc/systemd/system
sudo sed -i -e 's,/usr/bin/cri-dockerd,/usr/local/bin/cri-dockerd,' /etc/systemd/system/cri-docker.service
sudo systemctl daemon-reload
sudo systemctl enable --now cri-docker.socket

echo "install conntrack"
if [[ -z ${CONNTRACK_VERSION} ]];then
  CONNTRACK_VERSION="1.4.6"
fi
sudo yum install -y conntrack-tools-${CONNTRACK_VERSION}

echo "install crictl"
if [[ -z ${CRICTL_VERSION} ]];then
  CRICTL_VERSION="v1.28.0"
fi
cd /tmp
wget https://github.com/kubernetes-sigs/cri-tools/releases/download/${CRICTL_VERSION}/crictl-${CRICTL_VERSION}-linux-amd64.tar.gz
tar xvf crictl-${CRICTL_VERSION}-linux-amd64.tar.gz
sudo mv crictl /usr/local/bin/

echo "set selinux to permissive"
sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config

echo "set cgroupdriver"
cat << EOF | sudo tee /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl reload docker

echo 'install minikube'
if [[ -z ${KUBE_VERSION} ]];then
  KUBE_VERSION="v1.28.3"
fi
cd /tmp
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube start \
--kubernetes-version=${KUBE_VERSION} \
--driver=none

echo "setup addon"
minikube addons enable metrics-server

echo 'install kubectl'
WD=/tmp/kubectl
mkdir -p ${WD}
cd ${WD}
curl -LO https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

echo 'setup alias'
echo 'alias k="kubectl"' >> ~/.bash_profile
echo 'complete -F __start_kubectl k' >> ~/.bash_profile
echo 'source <(kubectl completion bash)' >> ~/.bash_profile

echo 'install helm'
if [[ -z ${HELM_VERSION} ]];then
  HELM_VERSION='v3.14.2'
fi
WD=/tmp/helm
mkdir -p ${WD}
cd ${WD}
curl "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" -o helm.tar.gz
tar -zxvf helm.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
