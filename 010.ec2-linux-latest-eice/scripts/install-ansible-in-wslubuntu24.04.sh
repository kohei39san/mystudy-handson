#!/bin/bash

sudo apt-get install python3-boto3 ansible openssh-server -y
sudo systemctl enable --now ssh.service

cp /etc/ssh/sshd_config /tmp/sshd_config.default
sudo cp ../conf/sshd_config /etc/ssh/sshd_config
sudo systemctl daemon-reload
sudo systemctl restart ssh.service
systemctl status ssh.service

cp /etc/ssh/ssh_host_ed25519_key.pub ~/.ssh/authorized_keys
sudo cp /etc/ssh/ssh_host_ed25519_key ~/.ssh/ssh_host_ed25519_key
sudo chown $(id -u):$(id -g) ~/.ssh/ssh_host_ed25519_key
nc -v -w 1 127.0.0.1 -z 22

mkdir ~/.aws
cp ../conf/aws.conf ~/.aws/config