#!/bin/bash -ex

echo "install kubernetes"

#echo "`ip -4 a show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'` `hostname`" | sudo tee -a /etc/hosts
echo "`hostname -i` `hostname`" | sudo tee -a /etc/hosts
cat << EOF | sudo tee -a /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF

#sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
if [[ -z ${K8S_VERSION} ]]; then
  K8S_VERSION="1.28.1"
fi
sudo yum install -y kubelet-${K8S_VERSION} kubeadm-${K8S_VERSION} kubectl-${K8S_VERSION} --disableexcludes=kubernetes
sudo swapoff -a
sudo systemctl start kubelet
sudo systemctl enable kubelet
cat << EOF | sudo tee /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl restart kubelet
sudo kubeadm init

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

echo 'setup master node'
kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml
CONTROL_PLANE=$(kubectl get node | grep control-plane | awk '{print $1}')
kubectl taint nodes $CONTROL_PLANE node-role.kubernetes.io/control-plane:NoSchedule-

echo 'setup kubectl'
echo 'alias k="kubectl"' >> ~/.bash_profile
echo 'complete -F __start_kubectl k' >> ~/.bash_profile
echo 'source <(kubectl completion bash)' >> ~/.bash_profile
